/* address: 0x00569814 */
/* name: CDXTexture__Helper_00569814 */
/* signature: void __cdecl CDXTexture__Helper_00569814(int param_1, void * param_2) */


void __cdecl CDXTexture__Helper_00569814(int param_1,void *param_2)

{
  int iVar1;
  int iVar2;

  iVar1 = param_1 - (int)param_2;
  iVar2 = 3;
  do {
    *(undefined4 *)(iVar1 + (int)param_2) = *(undefined4 *)param_2;
    param_2 = (void *)((int)param_2 + 4);
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return;
}
