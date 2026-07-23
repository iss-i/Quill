FUNCTION ZSMPL_FM_GET_ANTIFOAM_REQ_QTY.
*"----------------------------------------------------------------------
*"*"Local Interface:
*"  IMPORTING
*"     REFERENCE(IM_PRODUCT) TYPE  MATNR
*"     REFERENCE(IM_AUFNR) TYPE  AUFNR
*"     REFERENCE(IM_PHASE) TYPE  VORNR
*"     REFERENCE(IM_REQ_SUF) TYPE  CHAR30
*"     REFERENCE(IM_MAX_SUF) TYPE  CHAR30
*"     REFERENCE(IM_ID1) TYPE  CHAR30
*"  EXPORTING
*"     REFERENCE(EX_UOM) TYPE  MEINS
*"     REFERENCE(EX_REQ_QTY) TYPE  ERFMG
*"     REFERENCE(EX_MAX_QTY) TYPE  ERFMG
*"     REFERENCE(EX_MAT) TYPE  MATNR
*"----------------------------------------------------------------------
*--------------------------------------------------------------------------*
* Program Name    : ZSMPL_FM_GET_ANTIFOAM_REQ_QTY                          *
* Created by      : Ryan Kwok (RKWOK)                                      *
* Supplier        : Integration Solution Services Inc.                     *
* Created on      : Jun 1, 2026                                            *
*    Analyst:     : N/A                                                    *
* Purpose         : Use the product to obtain the BOM materials, using the *
*                   BOM materials find the required qty and max qty        *
* Returns the UOM of the Product, and the req/max/material for the BOM     *
*--------------------------------------------------------------------------*
* Description                  Transport     Programmer      Date          *
*--------------------------------------------------------------------------*
* Initial Development                        RKWOK          01/06/2026     *
*--------------------------------------------------------------------------*
* Modifications                                                            *
*--------------------------------------------------------------------------*

*--------------------------------------------------------------------------*

  DATA: lt_mat        TYPE /smpl/str_tt_matnr,
        lv_mat        TYPE matnr,
        lv_max        TYPE char30,
        lv_qty        TYPE char30,
        lt_keys       TYPE TABLE OF char30,
        lv_aufnr      TYPE aufnr.

  lv_aufnr = |{ im_aufnr ALPHA = IN }|.
*  SHIFT lv_aufnr LEFT DELETING LEADING '0'.

  CALL FUNCTION 'ZSMPL_FM_GET_MAT_DETAIL'
    EXPORTING
      im_matnr = im_product
    IMPORTING
      ex_uom   = ex_uom.

  CALL FUNCTION 'ZSMPL_FM_GET_PHASE_PO_ITEMSEBR'
    EXPORTING
      IV_ORDER  = lv_aufnr
      IV_PHASE  = im_phase
    IMPORTING
      ET_MATERIAL = lt_mat.



  LOOP AT lt_mat ASSIGNING FIELD-SYMBOL(<fs_mat>).
    DATA: lv_key_in  TYPE string,
          lv_key_out TYPE string.
    lv_key_in = condense( |{ <fs_mat> ALPHA = OUT }| ).

    lv_key_out = |{ lv_key_in }{ im_max_suf }|.
    APPEND lv_key_out TO lt_keys.
    lv_key_out = |{ lv_key_in }{ im_req_suf }|.
    APPEND lv_key_out TO lt_keys.
  ENDLOOP.

  SELECT identifier2, value FROM ztc_param_table
  FOR ALL ENTRIES IN @lt_keys
  WHERE identifier1 = @im_id1 AND identifier2 = @lt_keys-table_line
  INTO TABLE @DATA(lt_params).

  LOOP AT lt_mat ASSIGNING <fs_mat>.
    DATA: lv_key1_in TYPE string.
    lv_key1_in = condense( |{ <fs_mat> ALPHA = OUT }| ).

    DATA(lv_max_key) = |{ lv_key1_in }{ im_max_suf }|.
    DATA(lv_qty_key) = |{ lv_key1_in }{ im_req_suf }|.

    READ TABLE lt_params ASSIGNING FIELD-SYMBOL(<fs_max>)
         WITH KEY identifier2 = lv_max_key.
*    lv_max = COND #( WHEN sy-subrc = 0 THEN <fs_p>-value ELSE '' ).
    IF sy-subrc = 0. lv_max = <fs_max>-value. ENDIF.


    READ TABLE lt_params ASSIGNING FIELD-SYMBOL(<fs_req>)
         WITH KEY identifier2 = lv_qty_key.
*    lv_qty = COND #( WHEN sy-subrc = 0 THEN <fs_p>-value ELSE '' ).
    IF sy-subrc = 0. lv_qty = <fs_req>-value. ENDIF.

    lv_mat = <fs_mat>.

    EXIT.

  ENDLOOP.

  ex_max_qty = lv_max.
  ex_req_qty = lv_qty.
  ex_mat = lv_mat.


ENDFUNCTION.
