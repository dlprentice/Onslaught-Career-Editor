/* address: 0x005acd90 */
/* name: CDXTexture__BitstreamReadBitsWithJpegStuffing */
/* signature: int __stdcall CDXTexture__BitstreamReadBitsWithJpegStuffing(void * param_1, uint param_2, int param_3, int param_4) */


int CDXTexture__BitstreamReadBitsWithJpegStuffing
              (void *param_1,uint param_2,int param_3,int param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  byte *pbVar5;

  piVar1 = *(int **)((int)param_1 + 0x10);
  pbVar5 = *(byte **)param_1;
  iVar3 = *(int *)((int)param_1 + 4);
  if (piVar1[0x69] == 0) {
    for (; param_3 < 0x19; param_3 = param_3 + 8) {
      if (iVar3 == 0) {
        iVar3 = (**(code **)(piVar1[6] + 0xc))(piVar1);
        if (iVar3 == 0) {
          return 0;
        }
        pbVar5 = *(byte **)piVar1[6];
        iVar3 = ((undefined4 *)piVar1[6])[1];
      }
      uVar4 = (uint)*pbVar5;
      iVar3 = iVar3 + -1;
      pbVar5 = pbVar5 + 1;
      if (uVar4 == 0xff) {
        do {
          if (iVar3 == 0) {
            iVar3 = (**(code **)(piVar1[6] + 0xc))(piVar1);
            if (iVar3 == 0) {
              return 0;
            }
            pbVar5 = *(byte **)piVar1[6];
            iVar3 = ((undefined4 *)piVar1[6])[1];
          }
          uVar4 = (uint)*pbVar5;
          iVar3 = iVar3 + -1;
          pbVar5 = pbVar5 + 1;
        } while (uVar4 == 0xff);
        if (uVar4 != 0) {
          piVar1[0x69] = uVar4;
          goto LAB_005ace3d;
        }
        uVar4 = 0xff;
      }
      param_2 = param_2 << 8 | uVar4;
    }
  }
  else {
LAB_005ace3d:
    if (param_3 < param_4) {
      if (*(int *)(piVar1[0x70] + 8) == 0) {
        iVar2 = *piVar1;
        *(undefined4 *)(iVar2 + 0x14) = 0x75;
        (**(code **)(iVar2 + 4))(piVar1,0xffffffff);
        *(undefined4 *)(piVar1[0x70] + 8) = 1;
      }
      param_2 = param_2 << (0x19U - (char)param_3 & 0x1f);
      param_3 = 0x19;
    }
  }
  *(int *)((int)param_1 + 4) = iVar3;
  *(byte **)param_1 = pbVar5;
  *(uint *)((int)param_1 + 8) = param_2;
  *(int *)((int)param_1 + 0xc) = param_3;
  return 1;
}
