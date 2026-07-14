FUNCTION ZSMPL_FM_CALC_ADD_WEIGH.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IT_MATERIAL) TYPE  /SMPL/STR_TT_MATNR OPTIONAL
 *"     REFERENCE(IT_MAT_DESC) TYPE  /SMPL/STR_TT_MAKTX OPTIONAL
 *"     REFERENCE(IT_BATCH) TYPE  /SMPL/STR_TT_CHARG OPTIONAL
 *"     REFERENCE(IT_BOM_QUANTITY) TYPE  /SMPL/STR_TT_ERFMG OPTIONAL
 *"     REFERENCE(IT_ISSUED_QUANTITY) TYPE  /SMPL/STR_TT_ERFMG OPTIONAL
 *"     REFERENCE(IT_UOM) TYPE  /SMPL/STR_TT_ERFME OPTIONAL
 *"     REFERENCE(IT_MAT_ALT) TYPE  /SMPL/STR_TT_MATNR OPTIONAL
 *"     REFERENCE(IT_ITEM) TYPE  /SMPL/STR_TT_RSPOS OPTIONAL
 *"     REFERENCE(IV_INDEX) TYPE  SY-TABIX OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_REQ_QTY) TYPE  ERFMG
 *"     REFERENCE(EV_ITEM_NR) TYPE  APOSN
 *"     REFERENCE(EV_TOLERANCE_FLAG) TYPE  F
 *"  CHANGING
 *"     REFERENCE(CT_MATERIAL2) TYPE  /SMPL/STR_TT_MATNR OPTIONAL
 *"     REFERENCE(CT_MAT_DESC2) TYPE  /SMPL/STR_TT_MAKTX OPTIONAL
 *"     REFERENCE(CT_BATCH2) TYPE  /SMPL/STR_TT_CHARG OPTIONAL
 *"     REFERENCE(CT_MAT_REF) TYPE  /SMPL/STR_TT_MATNR OPTIONAL
 *"     REFERENCE(CT_BOM_QUANTITY2) TYPE  /SMPL/STR_TT_ERFMG OPTIONAL
 *"     REFERENCE(CT_ISSUED_QUANTITY2) TYPE  /SMPL/STR_TT_ERFMG OPTIONAL
 *"     REFERENCE(CT_EXP_DT2) TYPE  /SMPL/STR_TT_DATE OPTIONAL
 *"     REFERENCE(CT_ISSUED_TOTAL2) TYPE  /SMPL/STR_TT_ERFMG OPTIONAL
 *"     REFERENCE(CT_UOM) TYPE  /SMPL/STR_TT_ERFME OPTIONAL
 *"     REFERENCE(CT_ITEM) TYPE  /SMPL/STR_TT_RSPOS OPTIONAL
 *"     REFERENCE(CT_TOTAL_ISSUED_OG) TYPE  /SMPL/STR_TT_ERFMG OPTIONAL
 *"----------------------------------------------------------------------
 *----------------------------------------------------------------------*
 * Program Name    : ZSMPL_FM_CALC_ADD_WEIGH                         *
 * Project/Ticket  : SMPL / NA                                          *
 * Correction No.  : N/A                                                *
 * Change Request  : <CHG NO.>                                          *
 * Author          : KWVP774 Jason Craig                                *
 * Functional -                                                         *
 * Analyst         : KVHZ810 Frieda vd Merwe                            *
 * Create Date     : 14.04.2026                                         *
 * Description     : Calculate the additional weighout table's aggregate*
 *                   issued quantities based on the reference component *
 *                   + pass final tolerance check flag after weighout   *
 *                                                                      *
 *-------------------------MODIFICATION LOG-----------------------------*
 *                                                                      *
 *----------------------------------------------------------------------*
 
  DATA: lv_index           TYPE sy-tabix,
         lv_issued_qty1     TYPE erfmg,
         lv_issued_qty2     TYPE erfmg,
         lv_remaining       TYPE erfmg,
         lv_issued_total    TYPE erfmg,
         lv_total_issued_t1 TYPE erfmg,
         lv_total_issued_t2 TYPE erfmg,
         lv_bom_qty_t1      TYPE erfmg,
         lv_uom_t1          TYPE erfme,
         lv_item_t1         TYPE rspos.
 

  " LOOP through each row in Table 2
   LOOP AT ct_material2 INTO DATA(lv_mat2).
     lv_index = sy-tabix.
 
    " Read the reference component for this T2 row
     READ TABLE ct_mat_ref INTO DATA(lv_ref_comp) INDEX lv_index.
     IF sy-subrc <> 0 OR lv_ref_comp IS INITIAL.
       CONTINUE.
     ENDIF.
 
    " Sum all issued quantities in T1 for this reference component
     " Grab BOM qty from first T1 match (same requirement across batches)
 
    CLEAR: lv_total_issued_t1,
            lv_bom_qty_t1.
 
    DATA(lv_first_match) = abap_false.
 
    LOOP AT it_material INTO DATA(lv_mat1).
       DATA(lv_index1) = sy-tabix.
 
      IF lv_mat1 = lv_ref_comp.
 
        IF lv_first_match = abap_false.
           READ TABLE it_bom_quantity INTO lv_bom_qty_t1 INDEX lv_index1.
           IF sy-subrc <> 0.
             CLEAR lv_bom_qty_t1.
           ENDIF.
           ev_req_qty = lv_bom_qty_t1.
           lv_first_match = abap_true.
 
          READ TABLE it_issued_quantity INTO lv_issued_qty1 INDEX lv_index1.
           IF sy-subrc <> 0.
             CLEAR lv_issued_qty1.
           ENDIF.
           lv_total_issued_t1 = lv_total_issued_t1 + lv_issued_qty1.
 
          READ TABLE it_uom INTO lv_uom_t1 INDEX lv_index1.
           IF sy-subrc <> 0.
             CLEAR lv_uom_t1.
           ENDIF.
 
          READ TABLE it_item INTO lv_item_t1 INDEX lv_index1.
           IF sy-subrc <> 0.
             CLEAR lv_item_t1.
           ENDIF.
         ENDIF.
 
      ENDIF.
     ENDLOOP.
 
    " If no T1 match found, skip — reference component must exist in T1
     IF lv_first_match = abap_false.
       CONTINUE.
     ENDIF.
 
    " ---------------------------------------------------------------
     " PASS 2: Aggregate across ALL T2 rows for the same reference
     " component, excluding the current row being calculated.
     " ---------------------------------------------------------------
     CLEAR lv_total_issued_t2.
 
    LOOP AT ct_material2 INTO DATA(lv_mat2_inner).
       DATA(lv_index2) = sy-tabix.
 
      " Skip the current row itself
       IF lv_index2 = lv_index.
         CONTINUE.
       ENDIF.
 
      " Check if this other T2 row references the same component
       READ TABLE ct_mat_ref INTO DATA(lv_ref_comp_inner) INDEX lv_index2.
       IF sy-subrc <> 0 OR lv_ref_comp_inner IS INITIAL.
         CONTINUE.
       ENDIF.
 
      IF lv_ref_comp_inner = lv_ref_comp.
         READ TABLE ct_issued_quantity2 INTO lv_issued_qty2 INDEX lv_index2.
         IF sy-subrc <> 0.
           CLEAR lv_issued_qty2.
         ENDIF.
         lv_total_issued_t2 = lv_total_issued_t2 + lv_issued_qty2.
       ENDIF.
 
    ENDLOOP.
 
    " Remaining for this T2 row = BOM Required Qty (from T1) - T1 total issued - other T2 rows issued
     " ---------------------------------------------------------------
     lv_remaining = lv_bom_qty_t1 - lv_total_issued_t1 - lv_total_issued_t2.
 
    IF lv_remaining < 0.
       lv_remaining = 0.
     ENDIF.
 
    " Pass calculated remaining back as Required Amount for this T2 row
     MODIFY ct_bom_quantity2 FROM lv_remaining INDEX lv_index.
 
    " Issued Total for this T2 row = T1 total issued + ALL T2 rows issued (including current row)
     " ---------------------------------------------------------------
     READ TABLE ct_issued_quantity2 INTO lv_issued_qty2 INDEX lv_index.
     IF sy-subrc <> 0.
       CLEAR lv_issued_qty2.
     ENDIF.
 
    lv_issued_total = lv_total_issued_t1 + lv_total_issued_t2 + lv_issued_qty2.
 
    "Get original issued qty to use accurately for validation
     IF lv_index = iv_index.
       IF ct_total_issued_og[ lv_index ] IS INITIAL.
         ct_total_issued_og[ lv_index ] = lv_total_issued_t1 + lv_total_issued_t2.
       ENDIF.
     ENDIF.
 
    MODIFY ct_issued_total2 FROM lv_issued_total INDEX lv_index.
 
    MODIFY ct_uom FROM lv_uom_t1 INDEX lv_index.
 
    MODIFY ct_item FROM lv_item_t1 INDEX lv_index.
 
  ENDLOOP.
 
  " Final Tolerance Check for Required BOM Qty across T1 & T2
   " Flag values: 1 = Under, 2 = In range, 3 = Over
   ev_tolerance_flag = 2.
 
  LOOP AT ct_material2 INTO DATA(lv_tol_mat).
     DATA(lv_tol_index) = sy-tabix.
 
    " We use ct_issued_total2 (total issued T1+T2) vs original BOM from T1.
     " Re-derive BOM qty from T1 using the reference component.
     READ TABLE ct_mat_ref INTO DATA(lv_tol_ref) INDEX lv_tol_index.
     IF sy-subrc <> 0 OR lv_tol_ref IS INITIAL.
       CONTINUE.
     ENDIF.
 
    " Find the original BOM qty from T1 for this reference component
     DATA: lv_tol_bom_qty    TYPE erfmg,
           lv_tol_issued_tot TYPE erfmg,
           lv_tol_upper      TYPE erfmg,
           lv_tol_lower      TYPE erfmg.
 
    CLEAR lv_tol_bom_qty.
 
    LOOP AT it_material INTO DATA(lv_tol_mat1).
       IF lv_tol_mat1 = lv_tol_ref.
         READ TABLE it_bom_quantity INTO lv_tol_bom_qty INDEX sy-tabix.
         IF sy-subrc <> 0.
           CLEAR lv_tol_bom_qty.
         ENDIF.
         EXIT.  "BOM qty is same across batches
       ENDIF.
     ENDLOOP.
 
    IF lv_tol_bom_qty IS INITIAL.
       CONTINUE. " Cannot validate without a BOM qty
     ENDIF.
 
    " Read the aggregated issued total for this T2 row
     READ TABLE ct_issued_total2 INTO lv_tol_issued_tot INDEX lv_tol_index.
     IF sy-subrc <> 0.
       CLEAR lv_tol_issued_tot.
     ENDIF.
 
    " Calculate 1% tolerance band around BOM qty
     lv_tol_upper = lv_tol_bom_qty * '1.01'.
     lv_tol_lower = lv_tol_bom_qty * '0.99'.
 
    " Flag if total issued falls outside the tolerance range
     IF lv_tol_issued_tot < lv_tol_lower.
       ev_tolerance_flag = 1.
       EXIT.  "First Fail triggers sets flag
     ELSEIF lv_tol_issued_tot > lv_tol_upper.
       ev_tolerance_flag = 3.
       EXIT.  "First Fail triggers sets flag
     ELSE.
       ev_tolerance_flag = 2.
     ENDIF.
 
  ENDLOOP.
 

ENDFUNCTION.
