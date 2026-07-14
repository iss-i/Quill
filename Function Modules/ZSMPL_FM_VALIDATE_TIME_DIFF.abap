FUNCTION ZSMPL_FM_VALIDATE_TIME_DIFF.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_START_TIME) TYPE  /SMPL/STR_DE_START_TIME OPTIONAL
 *"     REFERENCE(IV_START_DATE) TYPE  /SMPL/STR_DE_START_DATE OPTIONAL
 *"     REFERENCE(IV_TIME_DIFF) TYPE  /SMPL/STR_DE_START_TIME OPTIONAL
 *"     REFERENCE(IV_TIME_MIN) TYPE  /SMPL/STR_DE_START_TIME OPTIONAL
 *"     REFERENCE(IV_TIME_MAX) TYPE  /SMPL/STR_DE_START_TIME OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_FAIL_FLAG) TYPE  F
 *"  EXCEPTIONS
 *"      INVALID_DATETIME
 *"      NO_PROCESS_START_TIME
 *"      TIME_EXCEEDS_LIMIT
 *"----------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_VALIDATE_TIME_DIFF                                      *
 * Created by      : Jason Craig (KWVP774)                                  *
 * Supplier        : Integration Solution Services (iSSi)                   *
 * Created on      : March 17, 2026                                         *
 * Purpose         : Export Process end time and validate time elapsed      *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development                         KWVP774       17/03/2026     *
 *--------------------------------------------------------------------------*
 
  DATA: lv_end_date  TYPE /SMPL/STR_DE_START_DATE,
         lv_end_time  TYPE /SMPL/STR_DE_START_TIME,
         timediff     TYPE /SMPL/STR_DE_START_TIME,
         lv_date_diff TYPE /SMPL/STR_DE_START_DATE,
         lv_max_time  TYPE /SMPL/STR_DE_START_TIME,  "KWVP774
         lv_min_time  TYPE /SMPL/STR_DE_START_TIME.  "KWVP774
 
  CONSTANTS: lc_min_time TYPE /SMPL/STR_DE_START_TIME VALUE '000000',  "KWVP774
              lc_max_time TYPE /SMPL/STR_DE_START_TIME VALUE '999999'.  "KWVP774
 
  "Get current system date and time
   lv_date_diff = sy-datlo.
   lv_end_date = sy-datlo.
   lv_end_time = sy-timlo.
 
  "Get Conditional Validation ranges
   IF iv_time_min IS INITIAL.
     lv_min_time = lc_min_time.
   ELSE.
     lv_min_time = iv_time_min.
   ENDIF.
 
  IF iv_time_max IS INITIAL.
     lv_max_time = lc_max_time.
   ELSE.
     lv_max_time = iv_time_max.
   ENDIF.
 
* Calculate Time difference
 
  IF iv_time_diff IS INITIAL.
   timediff = lv_end_time - iv_start_time.
   ELSE.
     timediff = iv_time_diff.
   ENDIF.
 
  IF iv_time_diff <= lv_max_time AND iv_time_diff >= lv_min_time.
     ev_fail_flag = 1.
   ELSEIF iv_time_diff > lv_max_time.
     ev_fail_flag = 2.
   ELSEIF iv_time_diff < lv_min_time.
     ev_fail_flag = '0.1'.
   ELSE.
     ev_fail_flag = 2.
     MESSAGE 'Time is outside of allowed range' TYPE 'S' DISPLAY LIKE 'W'.
 *    RAISE time_exceeds_limit.
   ENDIF.
 



ENDFUNCTION.
