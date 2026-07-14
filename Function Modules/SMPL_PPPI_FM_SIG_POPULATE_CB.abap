FUNCTION /smpl/pppi_fm_sig_populate_cb .
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IM_LABEL_ID) TYPE  CHAR1
 *"     REFERENCE(IM_STEP_NAME) TYPE  CHAR40 OPTIONAL
 *"     REFERENCE(IM_STEP_INDEX) TYPE  INT4
 *"     REFERENCE(IM_STEP_UUID) TYPE  /SMPL/STR_DE_SOG_UUID
 *"     REFERENCE(IM_CONTROL_RECIPE) TYPE  POC_DOCID
 *"     REFERENCE(IM_PHASE) TYPE  VORNR
 *"     REFERENCE(IM_PO_NR) TYPE  AUFNR OPTIONAL
 *"     REFERENCE(IM_PLANT) TYPE  WERKS_D OPTIONAL
 *"  EXCEPTIONS
 *"      TABLE_LOCK_NOT_POSSIBLE
 *"----------------------------------------------------------------------
 *---------------------------------------------------------------------*
 *  /SMPL/PPPI_FM_SIG_POPULATE_CB                                      *
 *---------------------------------------------------------------------*
 *     Author: JCRAIG                        Project: SMPL        *
 *     Date: Jan 02, 2025                   Release: 1.0.0             *
 *     Description:                                                    *
 *       Add CB signatures to signature validation structure           *
 *---------------------------------------------------------------------*
 *  Change History                                                     *
 *---------------------------------------------------------------------*
 *   MKIRK, 02/01/2025   - Initial release                             *
 *   JCRAIG, 15/07/2025  - Remove hardcoded text (MOD1)                *
 *                                                                     *
 *                                                                     *
 *---------------------------------------------------------------------*
   TYPES: BEGIN OF lty_mr_info,
            master_recipe  TYPE char12,
            recipe_counter TYPE plnal,
          END OF lty_mr_info.
 
  TYPES: BEGIN OF lty_step_seq,
            xstep_name   TYPE char40,
            step_index   TYPE int4,
            phase        TYPE vornr,
            created_date TYPE dats,
            step_uuid    TYPE /smpl/str_de_sog_uuid,
          END OF lty_step_seq.
 
  DATA: ls_mr_info          TYPE lty_mr_info,
         ls_structure        TYPE /smpl/pppi_pisst,
         lt_structure        TYPE STANDARD TABLE OF /smpl/pppi_pisst,
         lv_control_rec_dest TYPE phseq,
         l_date              TYPE dats,
         ls_sog_data         TYPE /smpl/mbr_sog,
         lt_sog_data         TYPE /smpl/mbr_sog_tt,
         lt_crid_data        TYPE /smpl/mbr_sog_tt,
         lv_unique_index     TYPE int4 VALUE 0,
         lv_date_active      TYPE datuv,
         lv_type             TYPE /smpl/mbr_ord_type,
         lv_key1             TYPE /smpl/mbr_key1.
 
  CONSTANTS: lc_proc_order          TYPE plnaw VALUE 'C',
              lc_prod_order          TYPE plnaw VALUE 'P',
              lc_validation_required TYPE char3 VALUE 'Yes',  " Remove hardcoding
              lc_cb_sig              TYPE char1 VALUE 'C',
              lc_mode                LIKE dd26e-enqmode VALUE 'E',  "MOD1
              lc_pisst_table         TYPE rstable-tabname VALUE '/SMPL/PPPI_PISST'.  "MOD1.
 
  " Initialize all variables
   CLEAR: ls_mr_info, ls_structure, lv_control_rec_dest,
          l_date, ls_sog_data, lv_unique_index, lv_date_active,
          lv_type, lv_key1.
 
  " Initialize internal tables
   REFRESH: lt_structure, lt_sog_data, lt_crid_data.
 
  "Check if the structure has already been built by a previous step
   SELECT COUNT(*) FROM /smpl/pppi_pisst
     WHERE ctrl_recipe = im_control_recipe
     AND po_nr = im_po_nr
     .
 
  "If the structure has not been built, first build it before updating entries
   IF sy-subrc NE 0.
     "Get the Master Recipe details
     SELECT SINGLE plnnr, plnal
       FROM afko
       WHERE afko~aufnr = @im_po_nr
       INTO @ls_mr_info.
 
    " Check if master recipe details were found - MOD1
     IF sy-subrc <> 0.
       RETURN.
     ENDIF.
 
    "Get the specific Control Recipe Destination
     SELECT SINGLE phseq
       FROM coch
       WHERE coch~crid = @im_control_recipe
       INTO @lv_control_rec_dest.
 
    " Check if control recipe destination was found
     IF sy-subrc <> 0.
        RETURN.
     ENDIF.
 
    "20250410 Add dynamic check for whether order is created using Routing/ProdOrd or MRecipe/ProcOrd
     SELECT SINGLE plnaw FROM afko
       WHERE aufnr = @im_po_nr
       INTO @DATA(lv_ordtype).
 
    " Check if order type was found - MOD1
     IF sy-subrc <> 0.
       " Proceed with initial value because Process Order is assumed
     ENDIF.
 
    "Get the actvie date for the SMPL table selections
     l_date = sy-datum.
 
    "20250107 JCRAIG change - Allow for XSteps added by Process Order through SiMPL (check PO 1st)
     " Check if type is Production or Process Order
     IF lv_ordtype = lc_prod_order.
       lv_type = /smpl/mbr_cl_common_api=>cv_type_prodorder.
     ELSE.
       lv_type = /smpl/mbr_cl_common_api=>cv_type_porder.
     ENDIF.
 
    "Get SOG Data from the SMPL Tables
     TRY.
         CALL METHOD /smpl/mbr_cl_db_service=>get_most_recent_smpl_data
           EXPORTING
             iv_type     = lv_type
             iv_plant    = im_plant
             iv_key1     = im_po_nr   "20250107 JCRAIG
             iv_datuv    = l_date
           IMPORTING
             et_sog_data = lt_sog_data.
       CATCH /smpl/mbr_cl_t100.
     ENDTRY.
 
    "Clean-up SOG data based on specific Control Recipe Destination
     LOOP AT lt_sog_data INTO ls_sog_data.
       IF ls_sog_data-dest_name = lv_control_rec_dest.
         APPEND ls_sog_data TO lt_crid_data.
       ENDIF.
     ENDLOOP.
 
    "Lock table prior to update - MOD1
     CALL FUNCTION 'ENQUEUE_E_TABLE'
       EXPORTING
         mode_rstable   = lc_mode
         tabname        = lc_pisst_table
       EXCEPTIONS
         foreign_lock   = 1
         system_failure = 2
         OTHERS         = 3.
 
    "Check for lock errors
     IF sy-subrc NE 0.
       RAISE table_lock_not_possible.
     ELSE.
 
      "Insert each entry into the EBR Structure table
       CLEAR ls_sog_data.
       LOOP AT lt_crid_data INTO ls_sog_data.
         DATA(lws_data) = VALUE /smpl/pppi_pisst( step_seqid  = ls_sog_data-step_index             step = ls_sog_data-xstep_name
                                                  step_uuid = ls_sog_data-uuid
                                                  master_recipe = ls_mr_info-master_recipe   recipe_group = ls_mr_info-recipe_counter
                                                  ctrl_recipe = im_control_recipe            po_nr = im_po_nr
                                                  created_date = ls_sog_data-created_date    phase = ls_sog_data-phase
                                                  validation_required = lc_validation_required ).  "Yes (MOD1)
         INSERT INTO /smpl/pppi_pisst VALUES lws_data.
 
      ENDLOOP.
 
    ENDIF.
 
    "Unlock table after update - MOD1
     CALL FUNCTION 'DEQUEUE_E_TABLE'
       EXPORTING
         mode_rstable = lc_mode
         tabname      = lc_pisst_table.
 
    "Get the EBR structure to assign the unique indexes
     SELECT * FROM /smpl/pppi_pisst
       WHERE po_nr = @im_po_nr
       AND ctrl_recipe = @im_control_recipe
       INTO @ls_structure.
       APPEND ls_structure TO lt_structure.
     ENDSELECT.
 
    " Check if any records were selected - MOD1
     IF sy-subrc <> 0 OR lines( lt_structure ) = 0.
       "Proceed with initial values so that structure-build is completed
     ENDIF.
 

    SORT lt_structure BY phase step_seqid ASCENDING.
 
    "Assign unique indexes to each step
     CLEAR ls_structure.
     LOOP AT lt_structure INTO ls_structure.
       lv_unique_index = lv_unique_index + 1000.
       UPDATE /smpl/pppi_pisst SET unique_seqid = @lv_unique_index
       WHERE po_nr = @im_po_nr
       AND ctrl_recipe = @im_control_recipe
       AND step_seqid = @ls_structure-step_seqid
       AND step = @ls_structure-step
       AND phase = @ls_structure-phase.
     ENDLOOP.
     CLEAR lv_unique_index.
   ENDIF.
 
  "If this is a Checked By,update the header and signature tag
   "don't update step_name if Header is empty
   IF im_label_id = lc_cb_sig. "C - MOD1
     IF im_step_name IS NOT INITIAL.
       UPDATE /smpl/pppi_pisst SET type = TEXT-002 step = im_step_name
        WHERE step_seqid = im_step_index
        AND ctrl_recipe = im_control_recipe
        AND phase = im_phase.
     ELSE.
       UPDATE /smpl/pppi_pisst SET type = TEXT-002
         WHERE step_seqid = im_step_index
         AND ctrl_recipe = im_control_recipe
         AND phase = im_phase.
     ENDIF.
 
  ENDIF.
 
ENDFUNCTION.
