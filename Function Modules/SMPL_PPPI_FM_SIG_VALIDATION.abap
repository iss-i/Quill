FUNCTION /smpl/pppi_fm_sig_validation.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IM_LABEL_ID) TYPE  CHAR1 OPTIONAL
 *"     REFERENCE(IM_STEP_NAME) TYPE  CHAR40 OPTIONAL
 *"     REFERENCE(IM_STEP_INDEX) TYPE  INT4
 *"     REFERENCE(IM_CONTROL_RECIPE) TYPE  POC_DOCID
 *"     REFERENCE(IM_PHASE) TYPE  VORNR
 *"     REFERENCE(IM_PO_NR) TYPE  AUFNR OPTIONAL
 *"     REFERENCE(IM_USERID) TYPE  XUBNAME
 *"     REFERENCE(IM_STEP_UUID) TYPE  /SMPL/MBR_SOG_UUID
 *"     REFERENCE(IM_CB_VALIDATE) TYPE  CHAR1 OPTIONAL
 *"     REFERENCE(IM_PLANT) TYPE  WERKS_D
 *"  EXCEPTIONS
 *"      CONTROL_RECIPE_INITIAL
 *"      USER_INITIAL
 *"      USER_NOT_SIGNED_INTO_SIG_TAB
 *"      USER_SIGNED_DONE_BY
 *"      PREDECESSOR_NOT_COMPLETED
 *"      REQ_EBR_STEPS_NOT_COMPLETED
 *"      USER_SIGNED_PERF_BY
 *"      XSTEP_CONFIG
 *"----------------------------------------------------------------------
 *---------------------------------------------------------------------*
 *  /SMPL/PPPI_FM_SIG_VALIDATION                                           *
 *---------------------------------------------------------------------*
 *     Author: JCRAIG                        Project: SMPL        *
 *     Date: Jan 02, 2025                   Release: 1.0.0             *
 *     Description:                                                    *
 *       Validate user signatures                                      *
 *---------------------------------------------------------------------*
 *  Change History                                                     *
 *---------------------------------------------------------------------*
 *   MKIRK, 02/01/2025   - Initial release                             *
 *   JCRAIG, 24/06/2025  - Remove hardcoded text (MOD1)                *
 *                                                                     *
 *                                                                     *
 *---------------------------------------------------------------------*
   TYPES: BEGIN OF lty_mr_info,
            master_recipe  TYPE char12,
            recipe_counter TYPE plnal,
          END OF lty_mr_info.
 
  DATA: ls_mr_info      TYPE lty_mr_info.
 
  DATA: ls_step_dep      TYPE /smpl/mbr_dep,
         lt_step_dep      TYPE /smpl/mbr_dep_tt,
         lt_crid_dep_data TYPE /smpl/mbr_dep_tt.
 
  CONSTANTS: lc_def_strt_seqid TYPE int4 VALUE '1000',
              lc_proc_order     TYPE plnaw VALUE 'C',
              lc_prod_order     TYPE plnaw VALUE 'P',
              lc_yes            TYPE char3 VALUE 'Yes',
              lc_true           TYPE char1 VALUE 'X',
              lc_cb_sig         TYPE char1 VALUE 'C',
              lc_perform        TYPE char1 VALUE 'P',
              lc_verify         TYPE char1 VALUE 'V'.
 
  DATA: lv_date_active      TYPE datuv,
         lv_type             TYPE /smpl/mbr_ord_type,
         lv_key1             TYPE /smpl/mbr_key1,
         l_date              TYPE dats,
         lv_control_rec_dest TYPE phseq.
 
  CLEAR:
   ls_mr_info,
   ls_step_dep,
   lt_step_dep,
   lt_crid_dep_data,
   lv_date_active,
   lv_type,
   lv_key1,
   l_date,
   lv_control_rec_dest.
 
  REFRESH:
     lt_step_dep, lt_crid_dep_data.
 
*----------------------------------------------------------------------*
 *Validate user ID & PI sheet number                                    *
 *----------------------------------------------------------------------*
   IF im_control_recipe IS INITIAL.
     RAISE control_recipe_initial.
   ENDIF.
 
  IF im_userid IS INITIAL.
     RAISE user_initial.
   ENDIF.
 
*----------------------------------------------------------------------*
 *Predecessor Step Validation                                           *
 *----------------------------------------------------------------------*
   "Get the Master Recipe details
   SELECT SINGLE plnnr, plnal
     FROM afko
     WHERE afko~aufnr = @im_po_nr
     INTO @ls_mr_info.
 
  " Check if master recipe details were found - MOD1
   IF sy-subrc <> 0.
     RAISE xstep_config.
   ENDIF.
 
  "Get the specific Control Recipe Destination
   SELECT SINGLE phseq
     FROM coch
     WHERE coch~crid = @im_control_recipe
     INTO @lv_control_rec_dest.
 
  " Check if control recipe destination was found
   IF sy-subrc <> 0.
     RAISE xstep_config.
   ENDIF.
 
  "20250410 Add dynamic check for whether order is created using Routing/ProdOrd or MRecipe/ProcOrd
   SELECT SINGLE plnaw FROM afko
     WHERE aufnr = @im_po_nr
     INTO @DATA(lv_ordtype).
 
  " Check if order type was found - MOD1
   IF sy-subrc <> 0.
     "proceed with initial value - Process order is assumed
   ENDIF.
 
  "Get the actvie date for the SMPL table selections
   l_date = sy-datum.
   "Allow for XSteps added by Process Order through SiMPL (check PO 1st)
   " Check if type is Production or Process Order - master recipe is checked automatically
   IF lv_ordtype = lc_prod_order.
     lv_type = /smpl/mbr_cl_common_api=>cv_type_prodorder.
   ELSE.
     lv_type = /smpl/mbr_cl_common_api=>cv_type_porder.
   ENDIF.
 
  "Get Dependency Data from the SMPL Tables
   TRY.
       CALL METHOD /smpl/mbr_cl_db_service=>get_most_recent_smpl_data
         EXPORTING
           iv_type     = lv_type
           iv_plant    = im_plant
           iv_key1     = im_po_nr
           iv_datuv    = l_date
         IMPORTING
           et_dep_data = lt_step_dep.
     CATCH /smpl/mbr_cl_t100.
   ENDTRY.
 
  "Clean-up Dependency data based on specific Control Recipe Destination and XStep UUID
   LOOP AT lt_step_dep INTO ls_step_dep.
     IF ls_step_dep-dest_name = lv_control_rec_dest AND ls_step_dep-dep_uuid = im_step_uuid.
       APPEND ls_step_dep TO lt_crid_dep_data.
     ENDIF.
   ENDLOOP.
 
  CLEAR ls_step_dep.
   LOOP AT lt_crid_dep_data INTO ls_step_dep.
 
    SELECT SINGLE *
       FROM /smpl/pppi_pisst
       INTO @DATA(ls_dep_status)
       WHERE step_uuid = @ls_step_dep-sog_UUID
       AND   ctrl_recipe = @im_control_recipe
       AND   validation_required = @lc_yes.   "Yes - MOD1
 
    IF sy-subrc = 0.
       IF ls_dep_status-completed NE lc_true.
         "MBR handles the dependencies
 *        MESSAGE TEXT-003 && ` ` && '( ' && ls_dep_status-step && ' )' TYPE 'S' DISPLAY LIKE 'E'.
 *        RAISE predecessor_not_completed.
       ENDIF.
     ENDIF.
   ENDLOOP.
 *----------------------------------------------------------------------*
 *Signature Table Validation                                           *
 *----------------------------------------------------------------------*
 *  Get PI Sheet Signatures from /smpl/pppi_pibsi
   SELECT SINGLE *
     FROM /smpl/pppi_pibsi
     INTO @DATA(ls_signature)
     WHERE pi_sheet = @im_control_recipe
     AND signature = @im_userid.
 
  IF sy-subrc <> 0.
     MESSAGE im_userid && ` ` && TEXT-004 TYPE 'S' DISPLAY LIKE 'E'.
     RAISE user_not_signed_into_sig_tab.
   ENDIF.
 

*----------------------------------------------------------------------*
 *Validation for Check By User id does not exist in Done By's           *
 *----------------------------------------------------------------------*
   DATA(lv_sigtype) = im_label_id.
   IF lv_sigtype EQ 'C' AND im_cb_validate EQ abap_true.
 **Getting the Unique Index for the passed Checkby
     SELECT SINGLE unique_seqid  INTO @DATA(lv_strt_uq_seqid) FROM /smpl/pppi_pisst
                                                        WHERE step_seqid  = @im_step_index
                                                        AND   step_uuid   = @im_step_uuid
                                                        AND   ctrl_recipe = @im_control_recipe
                                                        AND   phase       = @im_phase
                                                        AND   type        = @text-002.
     IF sy-subrc EQ 0.
       "Get the end Check by unique seq id for validating the Done by
       SELECT unique_seqid,type INTO TABLE @DATA(lt_cb_data) FROM /smpl/pppi_pisst
                                                             WHERE unique_seqid LT @lv_strt_uq_seqid
                                                             AND   ctrl_recipe  = @im_control_recipe
                                                             AND   phase        = @im_phase
                                                             AND   type         = @text-002.
       IF sy-subrc EQ 0.
         SORT lt_cb_data DESCENDING BY unique_seqid.
         DATA(lv_end_uq_seqid) = VALUE #( lt_cb_data[ 1 ]-unique_seqid OPTIONAL ).
       ELSEIF lt_cb_data[] IS INITIAL.
         "Incase of first check by defaulted to 1000
         lv_end_uq_seqid = lc_def_strt_seqid.
       ENDIF.
       "Check By's needs to be Validated
       SELECT COUNT(*) FROM /smpl/pppi_pisst UP TO 1 ROWS
                                                         WHERE ( unique_seqid LT @lv_strt_uq_seqid
                                                                 AND unique_seqid GT @lv_end_uq_seqid )
                                                         AND   ctrl_recipe  = @im_control_recipe
                                                         AND   phase        = @im_phase
                                                         AND   type         = @text-001
                                                         AND   sign_id      = @im_userid.
       IF sy-subrc EQ 0.
         MESSAGE im_userid && ` ` && TEXT-015 TYPE 'S' DISPLAY LIKE 'E'.  "MOD1
         RAISE user_signed_perf_by.
       ENDIF.
     ENDIF.
   ENDIF.
 
*----------------------------------------------------------------------*
 *Validation for final EBR Checked By signature (Mass Dependency Check) *
 *----------------------------------------------------------------------*
   "Get the last Unique Sequence ID from the EBR structure
   SELECT MAX( unique_seqid )
     INTO @DATA(lv_final_seqid)
     FROM /smpl/pppi_pisst
     WHERE ctrl_recipe = @im_control_recipe.
 
  IF sy-subrc <> 0.
     "MOD1 - Structure is empty if this fails
     RAISE xstep_config.
   ENDIF.
 

  "Get the last step in the structure
   SELECT SINGLE *
     FROM /smpl/pppi_pisst
     INTO @DATA(ls_final_step)
     WHERE ctrl_recipe = @im_control_recipe
     AND   unique_seqid = @lv_final_seqid.
 
  IF sy-subrc <> 0.
     "MOD1 - Structure is empty if this fails
     RAISE xstep_config.
   ENDIF.
 
  "If the current signature is the last EBR step, check all required steps for completion
   IF ls_final_step-step_uuid EQ im_step_uuid.
     SELECT *
       FROM /smpl/pppi_pisst
       INTO TABLE @DATA(lt_final_check)
       WHERE ctrl_recipe = @im_control_recipe
       AND   step_uuid <> @im_step_uuid
       AND   completed NE @lc_true                      "MOD1
       AND   validation_required EQ @lc_yes             "MOD1
       " JCRAIG 2024108 addition to check only WB, as PB only closed by WB
       AND   type = @text-002.
 
    IF sy-subrc = 0.
       MESSAGE TEXT-016 TYPE 'S' DISPLAY LIKE 'E'.  "MOD1
       RAISE req_ebr_steps_not_completed.
     ENDIF.
   ENDIF.
 
*----------------------------------------------------------------------*
 *Add MBR Dependency Validation Check       202251016  JCRAIG           *
 *----------------------------------------------------------------------*
   DATA lv_stype TYPE char1.
 
  IF im_label_id = lc_cb_sig.
     lv_stype = lc_verify.
   ELSE.
     lv_stype = lc_perform.
   ENDIF.
 

  CALL FUNCTION '/SMPL/MBR_DEP_VALI_SIGN'
     EXPORTING
       im_sig_type                  = lv_stype
       im_control_recipe            = im_control_recipe
       im_phase                     = im_phase
       im_aufnr                     = im_po_nr
       im_userid                    = im_userid
       im_step_uuid                 = im_step_uuid
       im_plant                     = im_plant
     EXCEPTIONS
       control_recipe_initial       = 1
       user_initial                 = 2
       user_not_signed_into_sig_tab = 3
       user_signed_done_by          = 4
       predecessor_not_completed    = 5
       req_ebr_steps_not_completed  = 6
       user_signed_perf_by          = 7
       OTHERS                       = 8.
 
  IF sy-subrc <> 0.
 * Implement suitable error handling here
     CASE sy-subrc.
       WHEN 1.
         RAISE control_recipe_initial.
       WHEN 2.
         RAISE user_initial.
       WHEN 3.
         MESSAGE im_userid && ` ` && TEXT-004 TYPE 'S' DISPLAY LIKE 'E'.
         RAISE user_not_signed_into_sig_tab.
       WHEN 4.
         RAISE user_signed_done_by.
       WHEN 5.
         MESSAGE TEXT-003 && ` ` && '( ' && sy-msgv1 && ' )' TYPE 'S' DISPLAY LIKE 'E'.
         RAISE predecessor_not_completed.
       WHEN 6.
         MESSAGE TEXT-016 TYPE 'S' DISPLAY LIKE 'E'.
         RAISE req_ebr_steps_not_completed.
       WHEN 7.
         MESSAGE im_userid && ` ` && TEXT-015 TYPE 'S' DISPLAY LIKE 'E'.
         RAISE user_signed_perf_by.
       WHEN 8.
         RAISE control_recipe_initial.
     ENDCASE.
   ENDIF.
 
  CLEAR:lv ZSMPL_FM_CALC_ADD_WEIGH _sigtype,
         lv_strt_uq_seqid,
         lv_end_uq_seqid,
         lt_cb_data[],
         lv_stype.
 
ENDFUNCTION.
