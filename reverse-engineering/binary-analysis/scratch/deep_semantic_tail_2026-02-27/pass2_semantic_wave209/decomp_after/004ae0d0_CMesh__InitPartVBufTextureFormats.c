/* address: 0x004ae0d0 */
/* name: CMesh__InitPartVBufTextureFormats */
/* signature: void __fastcall CMesh__InitPartVBufTextureFormats(void * param_1) */


void __fastcall CMesh__InitPartVBufTextureFormats(void *param_1)

{
  undefined4 uVar1;

  uVar1 = CVBufTexture__GetOrCreate(*(undefined4 *)param_1,0);
  *(undefined4 *)((int)param_1 + 4) = uVar1;
  CVBufTexture__SetVBFormat(0x152,8,0x24,4,1);
  CVBufTexture__SetIBFormat(0x65,8,2,1);
  return;
}
