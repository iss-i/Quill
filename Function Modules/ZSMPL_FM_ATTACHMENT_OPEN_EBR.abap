FUNCTION zsmpl_fm_attachment_open_ebr.
 *"----------------------------------------------------------------------
 *"*"Local Interface:
 *"  IMPORTING
 *"     REFERENCE(IM_ORDER) TYPE  AUFNR
 *"     REFERENCE(IM_MATNR) TYPE  MATNR18 OPTIONAL
 *"     REFERENCE(IM_CHARG) TYPE  CHARG_D OPTIONAL
 *"     REFERENCE(IM_FILENAME) TYPE  TEXT30
 *"     REFERENCE(IM_CREATED_DATE) TYPE  DATS
 *"     REFERENCE(IM_CREATED_TIME) TYPE  TIMS
 *"  EXCEPTIONS
 *"      INSPECTION_LOT_MISSING
 *"      FILENAME_NOT_FOUND
 *"      GOS_UTIL_NOT_INITIALIZED
 *"      LOAD_ATTACHMENTS_ERROR
 *"      FILE_CONVERSION_ERROR
 *"      FILE_LOAD_ERROR
 *"----------------------------------------------------------------------
 *======================================================================*
 * Program Name: ZSMPL_FM_ATTACHMENT_OPEN_EBR                           *
 * Author      : MKIRK                                                  *
 * Description : Download and execute attachments from the              *
 *               Generic Object Services for a single order via EBR     *
 *                                                                      *
 * Date Created: 07/07/2025                                             *
 *======================================================================*
 
  DATA: l_filename            TYPE string,
         l_aufnr               TYPE aufnr,
         l_temp_fname          TYPE text30,
         l_temp_length         TYPE i,
         l_curr_tzone          TYPE string,
         l_createdat_timestamp TYPE timestamp,
         lo_attach_service     TYPE REF TO /smpl/pppi_cl_attach_gos,
         lt_attachments        TYPE /smpl/pppi_cl_attach_gos=>tt_attachments,
         lt_data_tab           TYPE solix_tab,
         lx_attachment         TYPE /smpl/str_st_attach_srv,
         lx_media_resource     TYPE /iwbep/if_mgw_core_types=>ty_s_media_resource.
 
  CONSTANTS lc_error TYPE string VALUE 'E' ##NO_TEXT.
 
  " Exit without blocking PI Sheet if no file entered.
   IF im_filename IS INITIAL.
     EXIT.
   ENDIF.
 
  " Use order number for attachments
   "Check if order exists
   IF im_order IS NOT INITIAL.
     l_aufnr = im_order.
   ELSE.
     MESSAGE TEXT-001 TYPE lc_error RAISING inspection_lot_missing.
   ENDIF.
 
  " Get service instance for current inspection lot
   PERFORM get_service_instance
     USING
       l_aufnr
     CHANGING
       lo_attach_service.
 
  IF NOT lo_attach_service IS BOUND.
     MESSAGE TEXT-002 TYPE lc_error RAISING gos_util_not_initialized.
   ENDIF.
 
  " Get attachments for the inspection lot
   lo_attach_service->get_attachments(
     IMPORTING
       et_attachments = lt_attachments
   ).
 
  " Get timestamp because XSteps can't use timestamps
   l_curr_tzone = sy-zonlo.
   CONVERT DATE im_created_date TIME im_created_time INTO TIME STAMP l_createdat_timestamp TIME ZONE l_curr_tzone.
 
  " Check for the specified attachment
   LOOP AT lt_attachments ASSIGNING FIELD-SYMBOL(<fs_attachment>).
     l_temp_fname = CONV #( <fs_attachment>-filename ).
     l_temp_length = strlen( im_filename ).
     IF l_temp_fname(l_temp_length) EQ im_filename
         AND <fs_attachment>-createdat EQ l_createdat_timestamp.
       lx_attachment = <fs_attachment>.
       EXIT.
     ENDIF.
   ENDLOOP.
 
  IF sy-subrc NE 0 OR lx_attachment IS INITIAL.
     MESSAGE TEXT-003 TYPE lc_error RAISING filename_not_found.
   ENDIF.
 
  lo_attach_service->get_attachment_content(
     EXPORTING
       iv_id = lx_attachment-id
     IMPORTING
       ev_file_name = l_filename
       es_media_resource = lx_media_resource
   ).
 
* Gouthami Start of insertion for Po attachments EBR
   DATA(lcl_websocket) = NEW /smpl/ebr_cl_apc_ws( ).
   DATA: lo_socket    TYPE REF TO /smpl/ebr_cl_web_sock_hndl.
 
  DATA: lv_file_size     TYPE i,
         lv_base64        TYPE string,
         lv_line          TYPE string,
 *        lv_string,        TYPE string,
         lv_finstring        TYPE string,
         lv_output_length TYPE i,
         lv_filename      TYPE text30.
   lv_file_size = xstrlen( lx_media_resource-value ).
 
  CREATE OBJECT lo_socket.
   IF  lcl_websocket->gv_function = 'SMPL_EBR'.
 
    CALL FUNCTION 'SCMS_XSTRING_TO_BINARY'
       EXPORTING
         buffer        = lx_media_resource-value
       IMPORTING
         output_length = lv_output_length
       TABLES
         binary_tab    = lt_data_tab
       EXCEPTIONS
         OTHERS        = 1.
 
    IF sy-subrc NE 0.
       MESSAGE 'Error converting file to hex'(005) TYPE lc_error RAISING file_conversion_error.
     ENDIF.
 
    CALL FUNCTION 'SCMS_BINARY_TO_STRING'
       EXPORTING
         input_length = lv_output_length
       IMPORTING
         text_buffer  = lv_line
       TABLES
         binary_tab   = lt_data_tab
       EXCEPTIONS
         failed       = 1
         OTHERS       = 2.
     IF sy-subrc EQ 0.
       CONCATENATE lv_finstring lv_line INTO lv_finstring.
     ENDIF.
 
    CALL METHOD cl_http_utility=>encode_base64
       EXPORTING
         unencoded = lv_finstring
       RECEIVING
         encoded   = lv_base64.
 

      CONCATENATE  '<input name="DownloadAttachment" value="show_attachment_dialog">'
                    '<input name ="Filecontent"  value="' lv_base64 '">'
                    '<input name ="FileName"  value="' l_filename '">'
                     lcl_websocket->gv_request_string INTO DATA(lv_string).
 
      lo_socket->send_message( i_application_id = '/SMPL/EBR_AMC_MC'   "+PAM
                                i_channel_id     = '/ui5'
                                i_string         = lv_string
                                i_unique_id      = lcl_websocket->gv_unique_id ).
 
  ELSE.
 
    " Convert file data to hex string so it can be added to generic object services
     CALL FUNCTION 'SCMS_XSTRING_TO_BINARY'
       EXPORTING
         buffer     = lx_media_resource-value
       TABLES
         binary_tab = lt_data_tab
       EXCEPTIONS
         OTHERS     = 1.
 
    IF sy-subrc NE 0.
       MESSAGE 'Error converting file to hex'(005) TYPE lc_error RAISING file_conversion_error.
     ENDIF.
 

    cl_gui_frontend_services=>gui_download(
       EXPORTING
         filename                = l_filename
         filetype                = 'BIN'
       CHANGING
         data_tab                = lt_data_tab      " Transfer table for file contents
       EXCEPTIONS
         OTHERS                  = 1
     ).
     IF sy-subrc <> 0.
       MESSAGE ID sy-msgid TYPE sy-msgty NUMBER sy-msgno
         WITH sy-msgv1 sy-msgv2 sy-msgv3 sy-msgv4 RAISING file_load_error.
     ENDIF.
 
    cl_gui_frontend_services=>execute( document = l_filename ).
   ENDIF.
 
ENDFUNCTION.
