FUNCTION /smpl/pppi_fm_sig_add_db_cb .
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IM_CONTROL_RECIPE) TYPE  POC_DOCID
 *"     REFERENCE(IM_PHASE) TYPE  VORNR
 *"     REFERENCE(IM_STEP_IDX) TYPE  INT4
 *"     REFERENCE(IM_STEP) TYPE  CHAR30 OPTIONAL
 *"     REFERENCE(IM_SIGTYPE) TYPE  CHAR20 OPTIONAL
 *"     REFERENCE(IM_USERID) TYPE  XUBNAME OPTIONAL
 *"     REFERENCE(IM_DB_UP_DOWN) TYPE  CHAR1 OPTIONAL
 *"     REFERENCE(IM_VALIDATION_REQ) TYPE  CHAR3 OPTIONAL
 *"     REFERENCE(IM_STEP_UUID) TYPE  /SMPL/STR_DE_SOG_UUID OPTIONAL
 *"----------------------------------------------------------------------
 *---------------------------------------------------------------------*
 *  /SMPL/PPPI_FM_SIG_ADD_DB_CB                                        *
 *---------------------------------------------------------------------*
 *     Author: JCRAIG                        Project: SMPL        *
 *     Date: Jan 02, 2025                   Release: 1.0.0             *
 *     Description:                                                    *
 *       Add signatures to signature validation structure              *
 *---------------------------------------------------------------------*
 *  Change History                                                     *
 *---------------------------------------------------------------------*
 *   MKIRK, 02/01/2025   - Initial release                             *
 *   JCRAIG, 15/07/2025  - Remove hardcoded text & cleanup (MOD1)      *
 *                                                                     *
 *                                                                     *
 *---------------------------------------------------------------------*
   CONSTANTS: lc_def_strt_seqid TYPE int4 VALUE '1000',
              "MOD1
              lc_yes            TYPE char3 VALUE 'Yes',
              lc_no             TYPE char3 VALUE 'No',
              lc_below          TYPE char1 VALUE 'B',
              lc_cb_sig         TYPE char1 VALUE 'C',
              lc_type_o         TYPE char1 VALUE 'O',
              lc_true           TYPE char1 VALUE 'X',
              lc_no_dropdown    TYPE char1 VALUE '2'.
 
  "20241008 replaced step names with step UUIDs
 
  DATA(lv_sigtype) = im_sigtype.
   CASE lv_sigtype.
     WHEN ''.
       "Update Done By Step Name to Header of XStep
       IF im_step IS NOT INITIAL. " Don't update step name if default is empty
         UPDATE /smpl/pppi_pisst SET step = im_step
          WHERE step_seqid = im_step_idx
          AND ctrl_recipe = im_control_recipe
          AND phase = im_phase.
       ENDIF.
       IF im_db_up_down EQ '' .
         "Search for Unique Index and Insert above
         SELECT MIN( unique_seqid ) INTO @DATA(lv_unique_seqid) FROM /smpl/pppi_pisst
                                                          WHERE step_seqid  = @im_step_idx
                                                          AND   step_uuid   = @im_step_uuid
                                                          AND   ctrl_recipe = @im_control_recipe
                                                          AND   phase       = @im_phase.
         CHECK sy-subrc EQ 0 AND lv_unique_seqid IS NOT INITIAL.
         SELECT SINGLE * FROM /smpl/pppi_pisst INTO @DATA(ls_db_data) WHERE step_seqid   = @im_step_idx
                                                                    AND   unique_seqid = @lv_unique_seqid
                                                                    AND   step_uuid    = @im_step_uuid
                                                                    AND   ctrl_recipe  = @im_control_recipe
                                                                    AND   phase        = @im_phase.
         IF sy-subrc EQ 0.
           ls_db_data-unique_seqid = lv_unique_seqid - 1.
           ls_db_data-sign_id      = im_userid.
           ls_db_data-type         = TEXT-001.
           INSERT INTO /smpl/pppi_pisst VALUES ls_db_data.
           CLEAR:ls_db_data,
                 lv_unique_seqid.
         ENDIF.
       ELSEIF im_db_up_down EQ lc_below.  "B - MOD1
         "Search for Unique Index and Insert Below
         SELECT MAX( unique_seqid ) INTO @lv_unique_seqid  FROM /smpl/pppi_pisst
                                                          WHERE step_seqid  = @im_step_idx
                                                          AND   step_uuid   = @im_step_uuid
                                                          AND   ctrl_recipe = @im_control_recipe
                                                          AND   phase       = @im_phase.
         CHECK sy-subrc EQ 0 AND lv_unique_seqid IS NOT INITIAL.
         SELECT SINGLE * FROM /smpl/pppi_pisst INTO @ls_db_data WHERE step_seqid   = @im_step_idx
                                                             AND   unique_seqid = @lv_unique_seqid
                                                             AND   step_uuid   = @im_step_uuid
                                                             AND   ctrl_recipe  = @im_control_recipe
                                                             AND   phase        = @im_phase.
         IF sy-subrc EQ 0.
           ls_db_data-unique_seqid = lv_unique_seqid + 1.
           ls_db_data-sign_id      = im_userid.
           ls_db_data-type         = TEXT-001.
           INSERT INTO /smpl/pppi_pisst VALUES ls_db_data.
           CLEAR:ls_db_data,
                 lv_unique_seqid.
         ENDIF.
 
      ENDIF.
     WHEN lc_cb_sig.  "C - MOD1
       "Getting the Unique Index for the passed Checkby
       SELECT SINGLE unique_seqid  INTO @DATA(lv_strt_uq_seqid) FROM /smpl/pppi_pisst
                                                          WHERE step_seqid  = @im_step_idx
                                                          AND   step_uuid   = @im_step_uuid
                                                          AND   ctrl_recipe = @im_control_recipe
                                                          AND   phase       = @im_phase
                                                          AND   type        = @text-002.
       IF sy-subrc EQ 0.
         "Get the end Check by unique seq id for updating the corresponding Done by
         SELECT unique_seqid,type INTO TABLE @DATA(lt_cb_data) FROM /smpl/pppi_pisst
                                                               WHERE unique_seqid LT @lv_strt_uq_seqid
                                                               AND   ctrl_recipe  = @im_control_recipe
                                                               AND   type         = @text-002.
         IF sy-subrc EQ 0.
           SORT lt_cb_data DESCENDING BY unique_seqid.
           DATA(lv_end_uq_seqid) = VALUE #( lt_cb_data[ 1 ]-unique_seqid OPTIONAL ).
         ELSEIF lt_cb_data[] IS INITIAL.
           "Incase of first check by defaulted to 1000
           lv_end_uq_seqid = lc_def_strt_seqid.
         ENDIF.
         " Updating Checked By
         UPDATE /smpl/pppi_pisst SET sign_id   = im_userid
                                   completed = lc_true  "X - MOD1
                                                     WHERE step_seqid   = im_step_idx
                                                        AND   unique_seqid = lv_strt_uq_seqid
                                                        AND   step_uuid    = im_step_uuid
                                                        AND   ctrl_recipe  = im_control_recipe
                                                        AND   phase        = im_phase
                                                        AND   type         = TEXT-002.
         IF sy-subrc EQ 0 AND lv_strt_uq_seqid IS NOT INITIAL AND lv_end_uq_seqid IS NOT INITIAL.
           " Allow for the first XStep to be included for the completion of steps upon Checked By signature
           IF lv_end_uq_seqid = 1000.
             lv_end_uq_seqid = 1.
           ENDIF.
 
          SELECT * FROM /smpl/pppi_pisst INTO TABLE @DATA(lint_cd_db_data)
                                                             WHERE ( unique_seqid LT @lv_strt_uq_seqid
                                                                     AND unique_seqid GT @lv_end_uq_seqid )
                                                             AND   ctrl_recipe  = @im_control_recipe.
 
          IF sy-subrc EQ 0.
             LOOP AT lint_cd_db_data ASSIGNING FIELD-SYMBOL(<lfs_db_dat>).
               <lfs_db_dat>-completed = lc_true.   "X - MOD1
             ENDLOOP.
             CHECK lint_cd_db_data[] IS NOT INITIAL.
             MODIFY /smpl/pppi_pisst FROM TABLE lint_cd_db_data[].
           ENDIF.
         ENDIF.
       ENDIF.
 
    "Indicate when no validation is required
     WHEN lc_type_o.  "O - MOD1
       DATA lv_validation TYPE char3.
       IF im_validation_req = lc_no_dropdown.   "2 - MOD1
         lv_validation = lc_no.  "No (MOD1)
       ELSE.
         lv_validation = lc_yes.  "Yes (MOD2)
       ENDIF.
 
      UPDATE /smpl/pppi_pisst SET validation_required =  lv_validation
        WHERE step_seqid = im_step_idx
        AND ctrl_recipe = im_control_recipe
        AND phase = im_phase.
 

  ENDCASE.
   CLEAR:lv_sigtype,
         lv_strt_uq_seqid,
         lv_end_uq_seqid,
         lint_cd_db_data[].
 


ENDFUNCTION.
