/* address: 0x00590cde */
/* name: CDXTexture__Unk_00590cde */
/* signature: int __stdcall CDXTexture__Unk_00590cde(void * param_1, void * param_2, void * param_3) */


int CDXTexture__Unk_00590cde(void *param_1,void *param_2,void *param_3)

{
  int iVar1;
  int *piVar2;
  int *piVar3;
  bool bVar4;

  *(undefined4 *)param_3 = 0;
  iVar1 = 4;
  bVar4 = true;
  piVar2 = param_2;
  piVar3 = &DAT_0060c160;
  do {
    if (iVar1 == 0) break;
    iVar1 = iVar1 + -1;
    bVar4 = *piVar2 == *piVar3;
    piVar2 = piVar2 + 1;
    piVar3 = piVar3 + 1;
  } while (bVar4);
  if (!bVar4) {
    iVar1 = 4;
    bVar4 = true;
    piVar2 = &DAT_005eef8c;
    do {
      if (iVar1 == 0) break;
      iVar1 = iVar1 + -1;
      bVar4 = *(int *)param_2 == *piVar2;
      param_2 = (int *)((int)param_2 + 4);
      piVar2 = piVar2 + 1;
    } while (bVar4);
    if (!bVar4) {
      return -0x7fffbffe;
    }
  }
  *(void **)param_3 = param_1;
  (**(code **)(*(int *)param_1 + 4))(param_1);
  return 0;
}
