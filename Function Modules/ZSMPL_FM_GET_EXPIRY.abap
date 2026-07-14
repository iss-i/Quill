FUNCTION ZSMPL_FM_GET_EXPIRY.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_MATNR) TYPE  /SMPL/STR_TT_MATNR OPTIONAL
 *"     REFERENCE(IV_BATCH) TYPE  /SMPL/STR_TT_CHARG OPTIONAL
 *"     REFERENCE(IV_MATNR_ALT) TYPE  /SMPL/STR_TT_MATNR OPTIONAL
 *"     REFERENCE(IV_MAT) TYPE  MATNR OPTIONAL
 *"     REFERENCE(IV_BAT) TYPE  CHARG_D OPTIONAL
 *"     REFERENCE(IV_MAT_ALT) TYPE  MATNR OPTIONAL
 *"     REFERENCE(IV_CHAR_FLAG) TYPE  ABAP_BOOL OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_EXP_DATE) TYPE  /SMPL/STR_TT_DATE
 *"     REFERENCE(EV_FAIL) TYPE  F
 *"     REFERENCE(EV_EXP_DT) TYPE  /SMPL/STR_DE_DATE
 *"     REFERENCE(EV_EXP_DT_CHAR) TYPE  CHAR10
 *"  EXCEPTIONS
 *"      BATCH_EXPIRED
 *"      INVALID_BATCH
 *"----------------------------------------------------------------------
 *{   INSERT         ARSK902148                                        1
 *----------------------------------------------------------------------*
 * Program Name    : ZSMPL_FM_GET_EXPIRY                                *
 * Project/Ticket  : SMPL                                               *
 * Correction No.  : N/A                                                *
 * Change Request  : <CHG NO.>                                          *
 * Author          : JCRAIG Jason Craig                                 *
 * Functional                                                           *
 *    Analyst:     : <SAP ID> <Full Name>                               *
 * Create Date     : 21.04.2026                                         *
 * Description     : Retrieve Expiry Date for either a table of         *
 *                   material/batch values, or single material/batch    *
 *                   values and send a expiry fail flag for the signature*                                           *
 *----------------------------------------------------------------------*
 *-------------------------MODIFICATION LOG-----------------------------*
 *                                                                      *
 *----------------------------------------------------------------------*
 
  DATA: lv_matnr TYPE matnr,
         lv_batch TYPE mch1-charg,
         ls_tabix TYPE num1,
         lt_matnr TYPE /smpl/str_tt_matnr,
         lv_alt   TYPE matnr,
         lv_char_date    TYPE char10.
 
  CONSTANTS: lc_na TYPE char3 VALUE 'N/A'.
 
  "Ignore N/A values
   IF iv_mat = lc_na OR iv_bat = lc_na.
     RETURN.
   ENDIF.
 
  "Get Information for tabular material/batch values
   IF iv_mat IS INITIAL.
 
    lt_matnr = iv_matnr.
 
    LOOP AT lt_matnr INTO lv_matnr.  "iv_matnr
       ls_tabix = sy-tabix.
       READ TABLE iv_batch INDEX ls_tabix INTO lv_batch.
       IF sy-subrc <> 0.
         RAISE invalid_batch.
       ENDIF.
       "JCRAIG 20250929 - Allow for alternates
       READ TABLE iv_matnr_alt INDEX ls_tabix INTO lv_alt.
       IF sy-subrc = 0 AND lv_alt IS NOT INITIAL.
         lv_matnr = lv_alt.
       ENDIF.
       SELECT vfdat FROM mch1
         INTO @DATA(lv_exp_date)
         WHERE charg = @lv_batch
         AND matnr = @lv_matnr.
 
        "20260309 Expiry Validation
         IF lv_exp_date < sy-datum.
           ev_fail = 2.
         ELSE.
           ev_fail = 1.
         ENDIF.
 
      ENDSELECT.
 
      "Pass expiry date
       IF lv_matnr IS NOT INITIAL.
         APPEND lv_exp_date TO ev_exp_date.
       ENDIF.
       CLEAR lv_exp_date.
     ENDLOOP.
 
  "Get Information for tabular material/batch values
   ELSE.
     lv_matnr = iv_mat.
     lv_batch = iv_bat.
     "JCRAIG 20250929 - Allow for alternates
     IF iv_mat_alt IS NOT INITIAL.
       lv_matnr = iv_mat_alt.
     ENDIF.
 
    SELECT SINGLE vfdat FROM mch1
       INTO @DATA(lv_exp_dt)
       WHERE charg = @lv_batch
       AND matnr = @lv_matnr.
 
      IF sy-subrc <> 0.
         RAISE invalid_batch.
       ENDIF.
 
      "20260309 Expiry Validation
       IF lv_exp_dt < sy-datum.
         ev_fail = 2.
       ELSE.
         ev_fail = 1.
       ENDIF.
 
      "20240912 JCRAIG add functionality for char date
     IF iv_char_flag = abap_false.
       "Pass expiry date
       ev_exp_dt = lv_exp_dt.
 
    ELSE.
 
      lv_char_date = lv_exp_dt.
       CALL FUNCTION 'CONVERT_DATE_TO_EXTERNAL'
        EXPORTING
          DATE_INTERNAL                  = lv_exp_dt
        IMPORTING
          DATE_EXTERNAL                  = lv_char_date
        EXCEPTIONS
          DATE_INTERNAL_IS_INVALID       = 1
          OTHERS                         = 2
                 .
     ev_exp_dt_char = lv_char_date.
 
    ENDIF.
 
    CLEAR lv_exp_dt.
   ENDIF.
 

*}   INSERT
 ENDFUNCTION.
