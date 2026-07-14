FUNCTION zsmpl_fm_calc_issue_diff.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IM_ISSUED_DEF) TYPE  /SMPL/STR_TT_ERFMG OPTIONAL
 *"     REFERENCE(IM_ISSUED) TYPE  /SMPL/STR_TT_ERFMG OPTIONAL
 *"     REFERENCE(IM_INDEX) TYPE  SYST_INDEX OPTIONAL
 *"  EXPORTING
 *"     REFERENCE(EX_ISSUED_DIFF) TYPE  /SMPL/STR_TT_ERFMG
 *"----------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : ZSMPL_FM_CALC_ISSUE_DIFF                               *
 * Created by      : Jason Craig (KWVP774)                                  *
 * Supplier        : Integration Solution Services (iSSi)                   *
 * Created on      : March 17, 2026                                         *
 * Purpose         : Calculate Difference in Issued Qty for pre-weighed     *
 *                    components
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Programmer      Date          *
 *--------------------------------------------------------------------------*
 * Initial Development                         KWVP774       17/03/2026     *
 *--------------------------------------------------------------------------*
 
  ex_issued_diff = im_issued_def.
 
  " Check if any components were pre-weighed
   IF lines( im_issued_def ) > 0.
 
    " If index is provided, perform calculation at specific index
     IF im_index IS NOT INITIAL.
       " Issued difference cannot be less than 0 - cannot consume less than qty already issued
       ex_issued_diff[ im_index ] = COND #( WHEN im_issued[ im_index ] - im_issued_def[ im_index ] < 0 THEN 0
                                             ELSE  im_issued[ im_index ] - im_issued_def[ im_index ] ).
 
    "Else perform the calculation at each index
     ELSE.
 
      DO lines( im_issued_def ) TIMES.  "im_issued
         " Issued difference cannot be less than 0 - cannot consume less than qty already issued
         ex_issued_diff[ sy-index ] = COND #( WHEN im_issued[ sy-index ] - im_issued_def[ sy-index ] < 0 THEN 0
                                               ELSE  im_issued[ sy-index ] - im_issued_def[ sy-index ] ).
       ENDDO.
 
    ENDIF.
 
  ENDIF.
 

ENDFUNCTION.
