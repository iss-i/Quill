FUNCTION ZSMPL_FM_GET_DATE_AND_TIME.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_USER) TYPE  CHAR30 OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_DATE) TYPE  /SMPL/STR_DE_START_DATE
 *"     REFERENCE(EV_TIME) TYPE  /SMPL/STR_DE_START_TIME
 *"----------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_GET_DATE_AND_TIME                                      *
 * Created by      : Jason Craig (KWVP774)                                  *
 * Supplier        : Integration Solution Services (iSSi)                   *
 * Created on      : March 17, 2026                                         *
 * Purpose         : Output Local Date & Time                               *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development                         KWVP774       17/03/2026     *
 *--------------------------------------------------------------------------*
 

ev_date = sy-datlo.
 ev_time = sy-timlo.
 

ENDFUNCTION.
