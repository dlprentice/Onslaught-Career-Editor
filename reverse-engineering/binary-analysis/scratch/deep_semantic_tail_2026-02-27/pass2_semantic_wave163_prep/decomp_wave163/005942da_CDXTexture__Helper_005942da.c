/* address: 0x005942da */
/* name: CDXTexture__Helper_005942da */
/* signature: void __stdcall CDXTexture__Helper_005942da(void * param_1, int param_2, int param_3, int param_4, int param_5) */


void CDXTexture__Helper_005942da(void *param_1,int param_2,int param_3,int param_4,int param_5)

{
  uint uVar1;
  byte bVar2;
  uint uVar3;
  int iVar4;
  undefined1 *puVar5;
  byte *pbVar6;
  byte *pbVar7;

  uVar3 = *(uint *)param_1;
  if (*(char *)((int)param_1 + 8) == '\x03') {
    bVar2 = *(byte *)((int)param_1 + 9);
    if (bVar2 < 8) {
      if (bVar2 == 1) {
        pbVar7 = (byte *)(uVar3 + param_2 + -1);
        iVar4 = 7 - (uVar3 - 1 & 7);
        pbVar6 = (byte *)((uVar3 - 1 >> 3) + param_2);
        for (uVar1 = uVar3; uVar1 != 0; uVar1 = uVar1 - 1) {
          *pbVar7 = *pbVar6 >> ((byte)iVar4 & 0x1f) & 1;
          if (iVar4 == 7) {
            iVar4 = 0;
            pbVar6 = pbVar6 + -1;
          }
          else {
            iVar4 = iVar4 + 1;
          }
          pbVar7 = pbVar7 + -1;
        }
      }
      else if (bVar2 == 2) {
        pbVar7 = (byte *)(uVar3 + param_2 + -1);
        iVar4 = (3 - (uVar3 - 1 & 3)) * 2;
        pbVar6 = (byte *)((uVar3 - 1 >> 2) + param_2);
        for (uVar1 = uVar3; uVar1 != 0; uVar1 = uVar1 - 1) {
          *pbVar7 = *pbVar6 >> ((byte)iVar4 & 0x1f) & 3;
          if (iVar4 == 6) {
            iVar4 = 0;
            pbVar6 = pbVar6 + -1;
          }
          else {
            iVar4 = iVar4 + 2;
          }
          pbVar7 = pbVar7 + -1;
        }
      }
      else if (bVar2 == 4) {
        pbVar7 = (byte *)(uVar3 + param_2 + -1);
        iVar4 = (uVar3 & 1) << 2;
        pbVar6 = (byte *)((uVar3 - 1 >> 1) + param_2);
        for (uVar1 = uVar3; uVar1 != 0; uVar1 = uVar1 - 1) {
          *pbVar7 = *pbVar6 >> ((byte)iVar4 & 0x1f) & 0xf;
          if (iVar4 == 4) {
            iVar4 = 0;
            pbVar6 = pbVar6 + -1;
          }
          else {
            iVar4 = iVar4 + 4;
          }
          pbVar7 = pbVar7 + -1;
        }
      }
      *(undefined1 *)((int)param_1 + 9) = 8;
      *(undefined1 *)((int)param_1 + 0xb) = 8;
      *(uint *)((int)param_1 + 4) = uVar3;
    }
    if (*(char *)((int)param_1 + 9) == '\b') {
      pbVar7 = (byte *)(uVar3 + param_2 + -1);
      if (param_4 == 0) {
        iVar4 = uVar3 * 3;
        puVar5 = (undefined1 *)(iVar4 + -1 + param_2);
        for (; uVar3 != 0; uVar3 = uVar3 - 1) {
          *puVar5 = *(undefined1 *)((uint)*pbVar7 * 3 + 2 + param_3);
          puVar5[-1] = *(undefined1 *)((uint)*pbVar7 * 3 + 1 + param_3);
          puVar5[-2] = *(undefined1 *)(param_3 + (uint)*pbVar7 * 3);
          puVar5 = puVar5 + -3;
          pbVar7 = pbVar7 + -1;
        }
        *(undefined1 *)((int)param_1 + 0xb) = 0x18;
        *(undefined1 *)((int)param_1 + 8) = 2;
        *(undefined1 *)((int)param_1 + 10) = 3;
      }
      else {
        iVar4 = uVar3 * 4;
        puVar5 = (undefined1 *)(iVar4 + -1 + param_2);
        for (; uVar3 != 0; uVar3 = uVar3 - 1) {
          if ((int)(uint)*pbVar7 < param_5) {
            *puVar5 = *(undefined1 *)((uint)*pbVar7 + param_4);
          }
          else {
            *puVar5 = 0xff;
          }
          puVar5[-1] = *(undefined1 *)((uint)*pbVar7 * 3 + 2 + param_3);
          puVar5[-2] = *(undefined1 *)((uint)*pbVar7 * 3 + 1 + param_3);
          puVar5[-3] = *(undefined1 *)(param_3 + (uint)*pbVar7 * 3);
          puVar5 = puVar5 + -4;
          pbVar7 = pbVar7 + -1;
        }
        *(undefined1 *)((int)param_1 + 0xb) = 0x20;
        *(undefined1 *)((int)param_1 + 8) = 6;
        *(undefined1 *)((int)param_1 + 10) = 4;
      }
      *(undefined1 *)((int)param_1 + 9) = 8;
      *(int *)((int)param_1 + 4) = iVar4;
    }
  }
  return;
}
