FUNCTION ZSMPL_FM_LOAD_MAT_DESC.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IM_MATNR) TYPE  MATNR
 *"  EXPORTING
 *"     REFERENCE(EX_MAKTX) TYPE  MAKTX
 *"----------------------------------------------------------------------
 *--------------------------------------------------------------------------*
 * Function Module : /SMPL/PPPI_FM_LOAD_MAT_DESC                            *
 * Created by      : Jason Craig (JCRAIG)                                   *
 * Supplier        : Integration Solution Services (iSSi)                   *
 * Created on      : November 26, 2025                                      *
 * Purpose         : Get Material Description (Full Char40 length)          *
 *                                                                          *
 *--------------------------------------------------------------------------*
 *                           Change History                                 *
 *--------------------------------------------------------------------------*
 * Description                  Transport     Developer       Date          *
 *--------------------------------------------------------------------------*
 * Initial Development                        JCRAIG        26/11/2025      *
 *--------------------------------------------------------------------------*
 
  CONSTANTS: lc_na   TYPE char3 VALUE 'N/A',
              lc_lang TYPE langu VALUE 'E'.
 
  "Get material description for logon language
   SELECT SINGLE maktx FROM makt
      WHERE matnr = @im_matnr
        AND spras = @sy-langu
      INTO @ex_maktx.
 
  "If no description exists for logon language - retrieve English Description
   IF sy-subrc <> 0.
 
    SELECT SINGLE maktx FROM makt
      WHERE matnr = @im_matnr
       AND spras = @lc_lang
      INTO @ex_maktx.
 
    IF sy-subrc <> 0.
       ex_maktx = lc_na.
     ENDIF.
 
  ENDIF.
 

ENDFUNCTION.
