FUNCTION ZSMPL_FM_CHECK_EQUI_STATUS.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_SUBMITTED_STATUS) TYPE  /SMPL/STR_DE_STATUS
 *"       OPTIONAL
 *"     REFERENCE(IV_DEFAULT_STATUS) TYPE  /SMPL/STR_DE_STATUS OPTIONAL
 *"  EXCEPTIONS
 *"      DEVIATION_DETECTED
 *"----------------------------------------------------------------------
 *----------------------------------------------------------------------*
 * Program Name    : ZSMPL_FM_CHECK_EQUI_STATUS                         *
 * Project/Ticket  : SMPL / NA                                          *
 * Correction No.  : N/A                                                *
 * Change Request  : <CHG NO.>                                          *
 * Author          : <NA> Ethan Vletter                                 *
 * Functional -                                                         *
 * Analyst         : <SAP ID> <Full Name>                               *
 * Create Date     : 14.04.2026                                         *
 * Description     : Room Clearance ~ Validate equipment status against *
 *                   recommended default status. Raise deviation if     *
 *                   they do not match.                                 *
 *                                                                      *
 *-------------------------MODIFICATION LOG-----------------------------*
 *                                                                      *
 *----------------------------------------------------------------------*
 
" Compare the submitted status to the default/recommended status
 IF iv_submitted_status <> iv_default_status.
 
  " If result of the above comparision is not the same, raise this exception
   RAISE deviation_detected.
 
ENDIF.
 


ENDFUNCTION.
