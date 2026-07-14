FUNCTION /smpl/pppi_fm_sig_batch_sign.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IM_SIGNATURE) TYPE  CHAR30
 *"     REFERENCE(IM_PI_SHEET) TYPE  POC_DOCID
 *"  EXCEPTIONS
 *"      TABLE_LOCK_NOT_POSSIBLE
 *"      INSERT_FAILED
 *"----------------------------------------------------------------------
 *---------------------------------------------------------------------*
 *  /SMPL/PPPI_FM_SIG_BATCH_SIGN                                       *
 *---------------------------------------------------------------------*
 *     Author: JCRAIG                        Project: SMPL        *
 *     Date: Jan 02, 2025                   Release: 1.0.0             *
 *     Description:                                                    *
 *       Add signatures to EBR batch record signature table            *
 *---------------------------------------------------------------------*
 *  Change History                                                     *
 *---------------------------------------------------------------------*
 *   MKIRK, 02/01/2025   - Initial release                             *
 *   JCRAIG, 15/07/2025  - Remove hardcoded text/Cleanup (MOD1)        *
 *                                                                     *
 *                                                                     *
 *---------------------------------------------------------------------*
   DATA: lt_signatures TYPE TABLE OF /smpl/pppi_pibsi,
         ls_signatures LIKE LINE OF lt_signatures.
 
  CONSTANTS: lc_mode        LIKE  dd26e-enqmode VALUE 'E',  "MOD1
              lc_pibsi_table TYPE rstable-tabname VALUE '/SMPL/PPPI_PIBSI'.  "MOD1
 
  ls_signatures-signature = im_signature.
   ls_signatures-pi_sheet = im_pi_sheet.
 
  "Lock table prior to update
   CALL FUNCTION 'ENQUEUE_E_TABLE'
     EXPORTING
       mode_rstable   = lc_mode
       tabname        = lc_pibsi_table
     EXCEPTIONS
       foreign_lock   = 1
       system_failure = 2
       OTHERS         = 3.
 
  "Check for lock errors
   IF sy-subrc NE 0.
     RAISE table_lock_not_possible.
   ELSE.
     "Update the table entry with the new information or create a new entry
     INSERT INTO /smpl/pppi_pibsi VALUES @ls_signatures.
     IF sy-subrc NE 0.  "MOD1
       " Unlock table before raising exception
       CALL FUNCTION 'DEQUEUE_E_TABLE'
         EXPORTING
           mode_rstable = lc_mode
           tabname      = lc_pibsi_table.
 
      RAISE insert_failed.
     ENDIF.
   ENDIF.
 
  "Unlock table after update
   CALL FUNCTION 'DEQUEUE_E_TABLE'
     EXPORTING
       mode_rstable = lc_mode
       tabname      = lc_pibsi_table.
 

ENDFUNCTION.
