/* address: 0x005888ae */
/* name: CDXTexture__DeleteGdiObjectIfSet */
/* signature: void __fastcall CDXTexture__DeleteGdiObjectIfSet(void * param_1) */


void __fastcall CDXTexture__DeleteGdiObjectIfSet(void *param_1)

{
  if (*(HGDIOBJ *)param_1 != (HGDIOBJ)0x0) {
    DeleteObject(*(HGDIOBJ *)param_1);
  }
  return;
}
