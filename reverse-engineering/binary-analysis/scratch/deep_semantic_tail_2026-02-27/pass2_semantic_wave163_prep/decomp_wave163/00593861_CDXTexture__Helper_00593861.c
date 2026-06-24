/* address: 0x00593861 */
/* name: CDXTexture__Helper_00593861 */
/* signature: void __stdcall CDXTexture__Helper_00593861(void * param_1, void * param_2) */


void CDXTexture__Helper_00593861(void *param_1,void *param_2)

{
  undefined1 uVar1;
  int iVar2;

  if (*(char *)((int)param_1 + 9) == '\x10') {
    for (iVar2 = (uint)*(byte *)((int)param_1 + 10) * *(int *)param_1; iVar2 != 0;
        iVar2 = iVar2 + -1) {
      uVar1 = *(undefined1 *)param_2;
      *(undefined1 *)param_2 = *(undefined1 *)((int)param_2 + 1);
      *(undefined1 *)((int)param_2 + 1) = uVar1;
      param_2 = (void *)((int)param_2 + 2);
    }
  }
  return;
}
