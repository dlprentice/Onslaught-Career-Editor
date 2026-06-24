/* address: 0x005af670 */
/* name: CTexture__Helper_005af670 */
/* signature: void __stdcall CTexture__Helper_005af670(void * param_1) */


void CTexture__Helper_005af670(void *param_1)

{
  int iVar1;
  undefined4 *puVar2;
  bool bVar3;
  undefined4 *puVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  int iVar9;
  int *piVar10;
  undefined4 *puVar11;
  int iVar12;
  undefined1 uStack_10;

  puVar4 = (undefined4 *)(*(code *)**(undefined4 **)((int)param_1 + 4))(param_1,1,0xa0);
  iVar12 = *(int *)((int)param_1 + 0x130);
  *(undefined4 **)((int)param_1 + 0x1c8) = puVar4;
  *puVar4 = &LAB_005ae7f0;
  puVar4[1] = CTexture__Helper_005ae810;
  puVar4[2] = 0;
  if (iVar12 != 0) {
    puVar11 = *(undefined4 **)param_1;
    puVar11[5] = 0x19;
    (*(code *)*puVar11)(param_1);
  }
  if ((*(int *)((int)param_1 + 0x4c) == 0) || (bVar3 = true, *(int *)((int)param_1 + 0x140) < 2)) {
    bVar3 = false;
  }
  iVar12 = 0;
  if (0 < *(int *)((int)param_1 + 0x24)) {
    piVar10 = (int *)(*(int *)((int)param_1 + 0xdc) + 0x24);
    puVar11 = puVar4 + 0xd;
    do {
      iVar5 = (piVar10[-7] * *piVar10) / *(int *)((int)param_1 + 0x140);
      iVar6 = (piVar10[-6] * *piVar10) / *(int *)((int)param_1 + 0x140);
      iVar1 = piVar10[3];
      iVar7 = *(int *)((int)param_1 + 0x13c);
      iVar9 = *(int *)((int)param_1 + 0x138);
      puVar11[0xc] = iVar6;
      if (iVar1 == 0) {
        *puVar11 = &LAB_005ae900;
      }
      else if ((iVar5 == iVar9) && (iVar6 == iVar7)) {
        *puVar11 = &LAB_005ae8f0;
      }
      else {
        if (iVar5 * 2 == iVar9) {
          if (iVar6 == iVar7) {
            if ((bVar3) && (2 < (uint)piVar10[1])) {
              *puVar11 = CTexture__Helper_005af570;
            }
            else {
              *puVar11 = &LAB_005aea10;
            }
          }
          else {
            if ((iVar5 * 2 != iVar9) || (iVar6 * 2 != iVar7)) goto LAB_005af7b8;
            if ((bVar3) && (2 < (uint)piVar10[1])) {
              *puVar11 = CDXTexture__ConvertYccBlocksToRgb_Auto;
              puVar4[2] = 1;
            }
            else {
              *puVar11 = &LAB_005aea70;
            }
          }
        }
        else {
LAB_005af7b8:
          if ((iVar9 % iVar5 == 0) && (iVar1 = *(int *)((int)param_1 + 0x13c), iVar1 % iVar6 == 0))
          {
            uStack_10 = (undefined1)(iVar9 / iVar5);
            *puVar11 = &LAB_005ae910;
            *(undefined1 *)(iVar12 + 0x8c + (int)puVar4) = uStack_10;
            *(char *)(iVar12 + 0x96 + (int)puVar4) = (char)(iVar1 / iVar6);
          }
          else {
            puVar2 = *(undefined4 **)param_1;
            puVar2[5] = 0x26;
            (*(code *)*puVar2)(param_1);
          }
        }
        iVar1 = *(int *)((int)param_1 + 4);
        iVar9 = *(int *)((int)param_1 + 0x13c) * ((uint)(puVar4[2] == 1) * 2 + 1);
        iVar7 = CDXTexture__AlignUpToMultiple
                          (*(int *)((int)param_1 + 0x70),*(int *)((int)param_1 + 0x138));
        uVar8 = (**(code **)(iVar1 + 8))(param_1,1,iVar7,iVar9);
        puVar11[-10] = uVar8;
      }
      iVar12 = iVar12 + 1;
      puVar11 = puVar11 + 1;
      piVar10 = piVar10 + 0x15;
    } while (iVar12 < *(int *)((int)param_1 + 0x24));
  }
  return;
}
