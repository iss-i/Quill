FUNCTION /SMPL/PPPI_FM_SIG_DELETE_ENTR .
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_PI_SHEET) TYPE  POC_DOCID
 *"  EXCEPTIONS
 *"      TABLE_LOCK_NOT_POSSIBLE
 *"----------------------------------------------------------------------
 * Function Module : /SMPL/PPPI_FM_SIG_DELETE_ENTR                          *
 * Created by      : Gustav Grotius (GROTIUSGU)                             *
 * Supplier        : PLSS                                                   *
 * Created on      : October  30, 2025                                      *
 * Purpose         : Delete /SMPL/PPPI_PISST entries for PI Sheet once PI Sheet*
 *                   has been completed                                     *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development                                                      *
 *--------------------------------------------------------------------------*
   "Lock table prior to update
   CALL FUNCTION 'ENQUEUE_E_TABLE'
     EXPORTING
       mode_rstable   = 'E'
       tabname        = '/SMPL/PPPI_PISST'
     EXCEPTIONS
       foreign_lock   = 1
       system_failure = 2
       OTHERS         = 3.
 
  "Check for lock errors
   IF sy-subrc NE 0.
     RAISE table_lock_not_possible.
   ELSE.
   "Delete /SMPL/PPPI_PISST entries for PI Sheet once PI Sheet has been completed
         DELETE FROM /smpl/pppi_pisst WHERE ctrl_recipe = iv_pi_sheet.
   ENDIF.
 
  "Unlock table after update
   CALL FUNCTION 'DEQUEUE_E_TABLE'
     EXPORTING
       mode_rstable = 'E'
       tabname      = '/SMPL/PPPI_PISST'.
 

ENDFUNCTION.
