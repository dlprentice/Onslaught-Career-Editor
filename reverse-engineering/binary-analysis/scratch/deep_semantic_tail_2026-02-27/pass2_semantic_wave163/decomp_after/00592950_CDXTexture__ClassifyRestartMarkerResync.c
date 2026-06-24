/* address: 0x00592950 */
/* name: CDXTexture__ClassifyRestartMarkerResync */
/* signature: int __stdcall CDXTexture__ClassifyRestartMarkerResync(void * param_1, int param_2) */


int CDXTexture__ClassifyRestartMarkerResync(void *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;

  iVar3 = *(int *)param_1;
  iVar2 = *(int *)((int)param_1 + 0x1a4);
  *(undefined4 *)(iVar3 + 0x14) = 0x79;
  *(int *)(iVar3 + 0x18) = iVar2;
  *(int *)(iVar3 + 0x1c) = param_2;
  (**(code **)(iVar3 + 4))(param_1,0xffffffff);
  do {
    if (iVar2 < 0xc0) {
LAB_0059297f:
      iVar3 = 2;
    }
    else if ((((iVar2 < 0xd0) || (0xd7 < iVar2)) || (iVar2 == (param_2 + 1U & 7) + 0xd0)) ||
            (iVar2 == (param_2 + 2U & 7) + 0xd0)) {
      iVar3 = 3;
    }
    else {
      if ((iVar2 == (param_2 - 1U & 7) + 0xd0) || (iVar2 == (param_2 - 2U & 7) + 0xd0))
      goto LAB_0059297f;
      iVar3 = 1;
    }
    iVar1 = *(int *)param_1;
    *(undefined4 *)(iVar1 + 0x14) = 0x61;
    *(int *)(iVar1 + 0x18) = iVar2;
    *(int *)(iVar1 + 0x1c) = iVar3;
    (**(code **)(iVar1 + 4))(param_1,4);
    if (iVar3 == 1) {
      *(undefined4 *)((int)param_1 + 0x1a4) = 0;
      return 1;
    }
    if (iVar3 == 2) {
      iVar3 = CTexture__Helper_00592420(param_1);
      if (iVar3 == 0) {
        return 0;
      }
      iVar2 = *(int *)((int)param_1 + 0x1a4);
    }
    else if (iVar3 == 3) {
      return 1;
    }
  } while( true );
}
