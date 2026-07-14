FUNCTION zsmpl_fm_exc_time_complete_ebr .
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_AUFNR) TYPE  AUFNR
 *"     REFERENCE(IV_TIMER) TYPE  CHAR30 OPTIONAL
 *"     REFERENCE(IV_END_TIME) TYPE  TIMS OPTIONAL
 *"     REFERENCE(IV_END_DATE) TYPE  DATS OPTIONAL
 *"     REFERENCE(IV_COMPLETE) TYPE  CHAR1 OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_START_TIME) TYPE  TIMS
 *"     REFERENCE(EV_START_DATE) TYPE  DATS
 *"     REFERENCE(EV_ACTUAL_END_TIME) TYPE  TIMS
 *"     REFERENCE(EV_ACTUAL_END_DATE) TYPE  DATS
 *"     REFERENCE(EV_OLD_END_TIME) TYPE  TIMS
 *"     REFERENCE(EV_OLD_END_DATE) TYPE  DATS
 *"  EXCEPTIONS
 *"      TIMER_NOT_STARTED
 *"----------------------------------------------------------------------
 *  zsmpl_fm_exc_time_complete                                       *
 *---------------------------------------------------------------------*
 *     Author: MKIRK                        Project: OrionImpl.        *
 *     Date: Jan 02, 2025                   Release: 1.0.0             *
 *     Description:                                                    *
 *       Complete a timer, clear the z-table and close in the UI       *
 *---------------------------------------------------------------------*
 *  Change History                                                     *
 *---------------------------------------------------------------------*
 *   MKIRK, 02/01/2025   - Initial release                             *
 *   <UNM>, <MM/DD/2025  - <change details>                            *
 *                                                                     *
 *                                                                     *
 *---------------------------------------------------------------------*
 

  DATA: lv_end_time TYPE tims,
         lv_end_date TYPE dats.
 
  CONSTANTS: lc_plant TYPE werks_d VALUE '5120'.
 

  " Get default start time
   IF iv_end_time IS NOT INITIAL.
     lv_end_time = iv_end_time.
   ELSE.
     lv_end_time = sy-timlo.
   ENDIF.
 
  " Get default start date
   IF iv_end_date IS NOT INITIAL.
     lv_end_date = iv_end_date.
   ELSE.
     lv_end_date = sy-datlo.
   ENDIF.
 
  " Load excursion timer for order
   SELECT SINGLE * FROM /smpl/pppi_extim  "ztc_smpl_exc_tim
     WHERE aufnr = @iv_aufnr
       AND timer = @iv_timer
       AND plant = @lc_plant
     INTO @DATA(ls_exc_data).
 
  IF sy-subrc NE 0.
     MESSAGE 'No start time for order found'(001) TYPE gc_type_e RAISING timer_not_started.
   ENDIF.
 
  ev_start_time = ls_exc_data-start_time.
   ev_start_date = ls_exc_data-start_date.
 
  ev_actual_end_date = lv_end_date.
   ev_actual_end_time = lv_end_time.
 
*  *  *******
   "store old end date/time in XStep
   ev_old_end_date = ls_exc_data-end_date.
   ev_old_end_time = ls_exc_data-end_time.
 
  " Data found - update with real end date/time (20250916)
   IF iv_complete = abap_true.
    ls_exc_data-end_time = lv_end_time.
    ls_exc_data-end_date = lv_end_date.
   ENDIF.
 
  UPDATE /smpl/pppi_extim FROM ls_exc_data.
 
*    ******
 
  CALL FUNCTION 'ZSMPL_FM_EXC_TIME_CLOSE_EBR'
     EXPORTING
       iv_aufnr = iv_aufnr
       iv_timer = iv_timer.   "20250909 addition
 
ENDFUNCTION.
