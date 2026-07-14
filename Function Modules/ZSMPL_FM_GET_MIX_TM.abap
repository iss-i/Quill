FUNCTION ZSMPL_FM_GET_MIX_TM .
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_PHASE) TYPE  VORNR
 *"     REFERENCE(IV_ORDER) TYPE  AUFNR
 *"     REFERENCE(IV_STIMEM) TYPE  /SMPL/STR_DE_START_TIME OPTIONAL
 *"     REFERENCE(IV_TIMER_NAME) TYPE  CHAR20 OPTIONAL
 *"     REFERENCE(IV_STEP_NAME) TYPE  CHAR20 OPTIONAL
 *"     REFERENCE(IV_TIME_ELAPSED) TYPE  /SMPL/STR_DE_START_TIME
 *"       OPTIONAL
 *"----------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_GET_MIX_TM                                    *
 * Created by      : Jason Craig (JCRAIG)                                   *
 * Supplier        : Integration Solution Services (iSSi)                   *
 * Created on      : April 02, 2026                                         *
 * Purpose         : Update Start and End Time for process timer that       *
 *                    that allows for multiple start/stop entries           *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Developer       Date          *
 *--------------------------------------------------------------------------*
 * Initial Development                        JCRAIG           04/02/2026   *
 *--------------------------------------------------------------------------*
 
  "Get timer name, and update start time and elapsed time
   DATA(lv_timer) = iv_timer_name.
   IF iv_timer_name IS INITIAL.
       lv_timer = iv_step_name.
   ENDIF.
   IF sy-subrc = 0.
     UPDATE /SMPL/PPPI_PRCTM SET timer_name = lv_timer
                                 start_time = iv_stimem
                                 time_elapsed = iv_time_elapsed
                           WHERE aufnr = iv_order
                             AND vornr = iv_phase
                             AND timer_name = lv_timer.
   ENDIF.
 

ENDFUNCTION.
