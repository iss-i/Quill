FUNCTION ZSMPL_FM_SANIT_TYPE.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_IND) TYPE  CHAR1
 *"  EXPORTING
 *"     REFERENCE(EV_SANIT_TYPE) TYPE  CHAR10
 *"     REFERENCE(EV_EXP_DT) TYPE  CHAR10
 *"----------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_SANIT_TYPE                                    *
 * Created by      : Jason Craig (KWVP774)                                  *
 * Supplier        : Integration Solution Services (iSSi)                   *
 * Created on      : March 17, 2026                                         *
 * Purpose         : If the Sanitization type is Gamma-irradiated, default  *
 *                    cycle & expiry fields to 'N/A'                        *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development                         KWVP774       17/03/2026     *
 *--------------------------------------------------------------------------*
 
  CONSTANTS: lc_na TYPE char3 VALUE 'N/A'.
 
  "If dropdown option is 'Gamma-radiated', change exporting parameters to N/A
   IF iv_ind = '3'.
     ev_sanit_type = lc_na.
     ev_exp_dt = lc_na.
   ENDIF.
 



ENDFUNCTION.
