/* address: 0x00593526 */
/* name: CDXTexture__ReleasePngDecodeContextHandles */
/* signature: void __stdcall CDXTexture__ReleasePngDecodeContextHandles(void * param_1, void * param_2, void * param_3) */


void CDXTexture__ReleasePngDecodeContextHandles(void *param_1,void *param_2,void *param_3)

{
  int iVar1;
  undefined4 local_c;
  undefined4 local_8;

  iVar1 = 0;
  local_8 = (void *)0x0;
  local_c = 0;
  if (param_1 != (void *)0x0) {
    local_8 = *(void **)param_1;
  }
  if (param_2 != (void *)0x0) {
    iVar1 = *(int *)param_2;
  }
  if (param_3 != (void *)0x0) {
    local_c = *(int *)param_3;
  }
  if (local_8 != (void *)0x0) {
    CDXTexture__ResetPngDecodeContext(local_8,iVar1,local_c);
  }
  if (iVar1 != 0) {
    CDXTexture__Helper_0059cc68(iVar1);
    *(undefined4 *)param_2 = 0;
  }
  if (local_c != 0) {
    CDXTexture__Helper_0059cc68(local_c);
    *(undefined4 *)param_3 = 0;
  }
  if (local_8 != (void *)0x0) {
    CDXTexture__Helper_0059cc68((int)local_8);
    *(undefined4 *)param_1 = 0;
  }
  return;
}
