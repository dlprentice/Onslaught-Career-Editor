/* address: 0x005b1d50 */
/* name: CDXTexture__Unk_005b1d50 */
/* signature: void __stdcall CDXTexture__Unk_005b1d50(void * param_1, void * param_2) */


void CDXTexture__Unk_005b1d50(void *param_1,void *param_2)

{
  int iVar1;

  iVar1 = CDXTexture__Helper_005d08ad();
  *(int *)((int)param_2 + 0xc) = iVar1;
  if (iVar1 == 0) {
    iVar1 = *(int *)param_1;
    *(undefined4 *)(iVar1 + 0x14) = 0x3f;
    _strncpy((char *)(iVar1 + 0x18),"",0x50);
    (*(code *)**(undefined4 **)param_1)(param_1);
  }
  *(undefined1 **)param_2 = &LAB_005b1c70;
  *(undefined1 **)((int)param_2 + 4) = &LAB_005b1cd0;
  *(undefined1 **)((int)param_2 + 8) = &LAB_005b1d30;
  return;
}
