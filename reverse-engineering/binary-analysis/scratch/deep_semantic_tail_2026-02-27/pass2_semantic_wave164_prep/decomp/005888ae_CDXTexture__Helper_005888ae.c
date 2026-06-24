/* address: 0x005888ae */
/* name: CDXTexture__Helper_005888ae */
/* signature: void __fastcall CDXTexture__Helper_005888ae(void * param_1) */


void __fastcall CDXTexture__Helper_005888ae(void *param_1)

{
  if (*(HGDIOBJ *)param_1 != (HGDIOBJ)0x0) {
    DeleteObject(*(HGDIOBJ *)param_1);
  }
  return;
}
