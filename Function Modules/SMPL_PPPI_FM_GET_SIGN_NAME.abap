FUNCTION /smpl/pppi_fm_get_sign_name.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IV_USER) TYPE  XUBNAME
 *"  EXPORTING
 *"     REFERENCE(EV_NAME) TYPE  AD_NAMTEXT
 *"     REFERENCE(EV_AUTH) TYPE  XUCLASS
 *"     REFERENCE(EV_DATE) TYPE  DATS
 *"     REFERENCE(EV_TIME) TYPE  TIMS
 *"----------------------------------------------------------------------
 *---------------------------------------------------------------------*
 *  /SMPL/PPPI_FM_GET_SIGN_NAME                                        *
 *---------------------------------------------------------------------*
 *     Author: MKIRK                        Project: SMPL        *
 *     Date: Jan 02, 2025                   Release: 1.0.0             *
 *     Description:                                                    *
 *       Retrieves signatory's full name info                          *
 *---------------------------------------------------------------------*
 *  Change History                                                     *
 *---------------------------------------------------------------------*
 *   MKIRK, 02/01/2025   - Initial release                             *
 *   JCRAIG, 24/06/2025  - Remove hardcoded text (MOD1)                *
 *                                                                     *
 *                                                                     *
 *---------------------------------------------------------------------*
   SELECT SINGLE name_textc FROM user_addr
     WHERE bname = @iv_user
     INTO @DATA(lv_name).
 
  IF sy-subrc = 0.
     ev_name = lv_name.
   ELSE.
     ev_name = TEXT-012.  "MOD1
   ENDIF.
 
  "Select user class and ensure they are assigned to a user group
   SELECT SINGLE class FROM usr02
     WHERE bname = @iv_user
     INTO @DATA(lv_auth).
 
  IF sy-subrc = 0 AND lv_auth IS NOT INITIAL.
     ev_auth = lv_auth.
   ELSE.
     ev_auth = TEXT-017.
   ENDIF.
   CLEAR lv_name.
   CLEAR lv_auth.
 
  ev_date = sy-datum.
   ev_time = sy-timlo.
 


ENDFUNCTION.
