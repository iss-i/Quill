FUNCTION ZSMPL_FM_GET_DEFAULT_DATE_CHAR.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_DATE_CHAR) TYPE  CHAR8 OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EV_DATE_CHAR) TYPE  CHAR10
 *"  EXCEPTIONS
 *"      DATE_INTERNAL_IS_INVALID
 *"----------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_GET_DEFAULT_DATE_CHAR                         *
 * Created by      : Jason Craig (KWVP774)                                  *
 * Supplier        : Pangaea Solutions Inc. (PSi)                           *
 * Created on      : March 17, 2026                                         *
 * Purpose         : Convert date format yyyymmdd to Current User Format    *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development         ARSK902148     KWVP774        17/03/2026     *
 *--------------------------------------------------------------------------*
 
  DATA: lv_date_tmp LIKE sy-datum,
         lv_date     TYPE char10. "LIKE sy-datum.
 
  CONSTANTS: lc_date_def LIKE sy-datum VALUE '00000000'.
 
  IF iv_date_char IS INITIAL.
     lv_date_tmp = lc_date_def.
   ELSE.
     lv_date_tmp = iv_date_char.
   ENDIF.
 

CALL FUNCTION 'CONVERT_DATE_TO_EXTERNAL'
  EXPORTING
    DATE_INTERNAL                  = lv_date_tmp
  IMPORTING
    DATE_EXTERNAL                  = lv_date
  EXCEPTIONS
    DATE_INTERNAL_IS_INVALID       = 1
    OTHERS                         = 2
           .
 IF SY-SUBRC <> 0.
 * Implement suitable error handling here
   RAISE date_internal_is_invalid.
 ENDIF.
 
ev_date_char = lv_date.
 

ENDFUNCTION.
