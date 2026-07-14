FUNCTION zsmpl_fm_sol_tran_prm_config.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_STOR_VESSEL) TYPE  CHAR1
 *"  EXPORTING
 *"     REFERENCE(EV_INDICATOR) TYPE  CHAR1
 *"     REFERENCE(EV_INDICATOR_INT) TYPE  CHAR1
 *"----------------------------------------------------------------------
 *----------------------------------------------------------------------*
 * Program Name    : ZSMPL_FM_SOL_TRAN_PRM_CONFIG                       *
 * Project/Ticket  : AZGA                                               *
 * Correction No.  : N/A                                                *
 * Change Request  : <CHG NO.>                                          *
 * Author          : GGROTIUS Gustav Grotius                            *
 * Functional                                                           *
 *    Analyst:     : <SAP ID> <Full Name>                               *
 * Create Date     : 26.08.2025                                         *
 * Description     : XStep provides a dropdown select for:              *
 *                   - 1: Bioreactor                                    *
 *                   - 2: Tank or Bags                                  *
 *                   - 3: Bottles                                       *
 *                   - 4: Tanks or Bags and Bottles                     *
 *                   If the user selects option 2 or 4, make the output *
 *                   variable 1. This variable is passed as a output    *
 *                   param in the XStep and sent to Goods Issue authored*
 *                   below Solution Transfer to activate the step using *
 *                   IV_ACTIVE through MBR                              *
 *                                                                      *
 *-------------------------MODIFICATION LOG-----------------------------*
 *----------------------------------------------------------------------*
 
  IF iv_stor_vessel = 3 OR iv_stor_vessel = 4.
     ev_indicator = 1.
   ELSE.
     ev_indicator = 2.
   ENDIF.
 
  IF iv_stor_vessel = 0 OR iv_stor_vessel = 1 OR iv_stor_vessel = 3.
     ev_indicator_int = 2.
   ELSE.
     ev_indicator_int = 1.
   ENDIF.
 


ENDFUNCTION.
