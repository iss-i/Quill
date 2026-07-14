FUNCTION zsmpl_fm_exc_time_create_ebr.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_WERKS) TYPE  WERKS_D
 *"     REFERENCE(IV_AUFNR) TYPE  AUFNR
 *"     REFERENCE(IV_NUM_MINS) TYPE  INT4
 *"     REFERENCE(IV_TIMER) TYPE  CHAR30
 *"     REFERENCE(IV_TIMER_TYPE) TYPE  CHAR30 OPTIONAL
 *"     REFERENCE(IV_START_TIME) TYPE  TIMS OPTIONAL
 *"     REFERENCE(IV_START_DATE) TYPE  DATS OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_END_TIME) TYPE  TIMS
 *"     REFERENCE(EV_END_DATE) TYPE  DATS
 *"  CHANGING
 *"     REFERENCE(CV_START_DATE) TYPE  DATS OPTIONAL
 *"     REFERENCE(CV_START_TIME) TYPE  TIMS OPTIONAL
 *"  EXCEPTIONS
 *"      DATE_CALC_ERROR
 *"      HOURGLASS_NOT_CONFIGURED
 *"      ERROR_TABLE_LOCK
 *"----------------------------------------------------------------------
 *---------------------------------------------------------------------*
 *  ZSMPL_FM_EXC_TIME_CREATE_EBR                                       *
 *---------------------------------------------------------------------*
 *     Author: MKIRK                        Project: OrionImpl.        *
 *     Date: Jan 02, 2025                   Release: 1.0.0             *
 *     Description:                                                    *
 *       Create a new timer in the z-table and open it in the UI       *
 *---------------------------------------------------------------------*
 *  Change History                                                     *
 *---------------------------------------------------------------------*
 *   MKIRK, 02/01/2025   - Initial release                             *
 *   KWVP774, 03/16/2026  - Add exporting date/time values  (MOD1)     *
 *   <UNM>, <MM/DD/2025  - <change details>                            *
 *                                                                     *
 *                                                                     *
 *---------------------------------------------------------------------*
 
  DATA: lv_start_time TYPE tims,
         lv_start_date TYPE dats,
         lv_end_time   TYPE tims,
         lv_end_date   TYPE dats,
         lv_time_limit TYPE tims.
 
  DATA: lv_num_days       TYPE int4,
         lv_num_hours      TYPE int4,
         lv_num_mins       TYPE int4,
         lv_time_remaining TYPE int4,
         lv_char_hours     TYPE char2,
         lv_char_mins      TYPE char2.
 
  CONSTANTS: lc_mode LIKE dd26e-enqmode VALUE 'E',
              lc_extim_table  TYPE rstable-tabname VALUE '/SMPL/PPPI_EXTIM'.
 
  " Get default start time
   IF iv_start_time IS NOT INITIAL.
     lv_start_time = iv_start_time.
   ELSE.
     lv_start_time = sy-timlo.
     cv_start_time = lv_start_time.  "MOD1
   ENDIF.
 
  " Get default start date
   IF iv_start_date IS NOT INITIAL.
     lv_start_date = iv_start_date.
   ELSE.
     lv_start_date = sy-datlo.
     cv_start_date = lv_start_date.  "MOD1
   ENDIF.
 
  " Setup time value from number of minutes
   lv_time_remaining = iv_num_mins.
 
  " Get number of days, then get number of hours remaining
   lv_num_days = lv_time_remaining DIV 1440.
   lv_time_remaining = lv_time_remaining MOD 1440.
 
  " Get number of hours, then get number of minutes remaining
   lv_num_hours = lv_time_remaining DIV 60.
   lv_time_remaining = lv_time_remaining MOD 60.
 
  " Get number of minutes
   lv_num_mins = lv_time_remaining.
 
  " Get number of minutes and hours
   UNPACK lv_num_hours TO lv_char_hours.
   UNPACK lv_num_mins TO lv_char_mins.
 
  " Create time to add in correct format
   CONCATENATE lv_char_hours lv_char_mins '00' INTO lv_time_limit.
 
  " Add time to the start time to get end time.
   CALL FUNCTION 'C14B_ADD_TIME'
     EXPORTING
       i_startdate   = lv_start_date
       i_starttime   = lv_start_time
       i_addtime     = lv_time_limit
     IMPORTING
       e_enddate     = lv_end_date
       e_endtime     = lv_end_time
     EXCEPTIONS
       error_message = 1.
 
  IF sy-subrc NE 0.
     MESSAGE 'Error calculating end date'(005) TYPE gc_type_e RAISING date_calc_error.
   ENDIF.
 
  " Add days after new time is set up
   lv_end_date = lv_end_date + lv_num_days.
 
CALL FUNCTION 'ENQUEUE_E_TABLE'
  EXPORTING
    MODE_RSTABLE         = lc_mode
    TABNAME              = lc_extim_table
  EXCEPTIONS
    FOREIGN_LOCK         = 1
    SYSTEM_FAILURE       = 2
    OTHERS               = 3
           .
 IF SY-SUBRC <> 0.
 * Implement suitable error handling here
 ENDIF.
 

  IF sy-subrc <> 0.
     MESSAGE 'Error locking excursion timer table'(004) TYPE gc_type_e RAISING error_table_lock.
   ENDIF.
 
  " Check if data needs to be inserted or modified
   SELECT SINGLE * FROM /smpl/pppi_extim
     WHERE plant = @iv_werks
       AND aufnr = @iv_aufnr
       AND timer = @iv_timer
      INTO @DATA(ls_exc_time).
 
  IF sy-subrc NE 0.
     " Data not found
     ls_exc_time = VALUE /smpl/pppi_extim(
       aufnr = iv_aufnr
       plant = iv_werks
       timer = iv_timer
       timer_type = iv_timer_type
       start_time = lv_start_time
       start_date = lv_start_date
       end_time = lv_end_time
       end_date = lv_end_date
     ).
 
    INSERT INTO /smpl/pppi_extim VALUES ls_exc_time.
   ELSE.
     " Data found
     ls_exc_time-start_time = lv_start_time.
     ls_exc_time-start_date = lv_start_date.
     ls_exc_time-end_time = lv_end_time.
     ls_exc_time-end_date = lv_end_date.
 
    UPDATE /smpl/pppi_extim FROM ls_exc_time.
   ENDIF.
 
  CALL FUNCTION 'DEQUEUE_E_TABLE'
  EXPORTING
    MODE_RSTABLE         = lc_mode
    TABNAME              = lc_extim_table
  EXCEPTIONS
    FOREIGN_LOCK         = 1
    SYSTEM_FAILURE       = 2
    OTHERS               = 3
           .
 
  IF sy-subrc <> 0.
     MESSAGE 'Error unlocking excursion timer table'(003) TYPE gc_type_e RAISING error_table_lock.
   ENDIF.
 
  CALL FUNCTION 'ZSMPL_FM_EXC_TIME_REOPEN_EBR'
     EXPORTING
       iv_aufnr                 = iv_aufnr
       iv_werks                 = iv_werks
       iv_end_time              = lv_end_time
       iv_end_date              = lv_end_date
       iv_timer                 = iv_timer
     EXCEPTIONS
       hourglass_not_configured = 1.
 
  IF sy-subrc NE 0.
     RAISE hourglass_not_configured.
   ENDIF.
 
  ev_end_time = lv_end_time.
   ev_end_date = lv_end_date.
 
ENDFUNCTION.
