FUNCTION ZSMPL_FM_GET_EXP_DATE .
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_DAYSADD) TYPE  CHAR3
 *"     REFERENCE(IV_SDATE) TYPE  /SMPL/STR_DE_START_DATE OPTIONAL
 *"     REFERENCE(IV_ORDER) TYPE  AUFNR OPTIONAL
 *"     REFERENCE(IV_PHASE) TYPE  VORNR OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_END_DATE) TYPE  /SMPL/STR_DE_START_DATE
 *"  EXCEPTIONS
 *"      PAST_DATES_NOT_ALLOWED
 *"----------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_GET_EXP_DATE                                  *
 * Created by      : Carlos Redekopp                                        *
 * Supplier        : ISSI                                                   *
 * Created on      : July 24, 2024                                          *
 * Purpose         : Print Expiry date based on input added days to current date*
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development                       Carlos Redekopp  07/25/2024    *
 *--------------------------------------------------------------------------*
 
DATA:
       lw_daysadd TYPE int3,
       lw_start_date TYPE /SMPL/STR_DE_START_DATE.
 
  IF iv_sdate IS INITIAL OR iv_sdate = 0. "value comes in as 0
     lw_start_date = sy-datum.
   ELSE.
     lw_start_date = iv_sdate.
   ENDIF.
 
  lw_daysadd = iv_daysadd.
 
  ev_end_date = lw_start_date + lw_daysadd.
 
  IF ev_end_date < sy-datum.
     MESSAGE 'Expiry Date cannot be in the past'(004) TYPE 'E' RAISING PAST_DATES_NOT_ALLOWED. "TYPE gc_type_e RAISING PAST_DATES_NOT_ALLOWED.
   ENDIF.
 

ENDFUNCTION.
