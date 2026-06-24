/* address: 0x005951d9 */
/* name: CDXTexture__ZeroDecodeWorkspace16Dwords */
/* signature: void __stdcall CDXTexture__ZeroDecodeWorkspace16Dwords(int param_1, void * param_2) */


void CDXTexture__ZeroDecodeWorkspace16Dwords(int param_1,void *param_2)

{
  int iVar1;

  for (iVar1 = 0x10; iVar1 != 0; iVar1 = iVar1 + -1) {
    *(undefined4 *)param_2 = 0;
    param_2 = (undefined4 *)((int)param_2 + 4);
  }
  return;
}
