/* address: 0x005b6cf0 */
/* name: CDXTexture__InitUpsamplerDispatch */
/* signature: void __stdcall CDXTexture__InitUpsamplerDispatch(void * param_1) */


void CDXTexture__InitUpsamplerDispatch(void *param_1)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  int *piVar5;
  int unaff_EDI;
  undefined4 *puVar6;
  int iVar7;

  puVar4 = (undefined4 *)(*(code *)**(undefined4 **)((int)param_1 + 4))(param_1,1,0x34);
  iVar7 = *(int *)((int)param_1 + 0xbc);
  *(undefined4 **)((int)param_1 + 0x16c) = puVar4;
  *puVar4 = &DAT_005b0ed0;
  puVar4[1] = &LAB_005b62f0;
  puVar4[2] = 0;
  if (iVar7 != 0) {
    puVar6 = *(undefined4 **)param_1;
    puVar6[5] = 0x19;
    (*(code *)*puVar6)(param_1);
  }
  iVar7 = 0;
  if (0 < *(int *)((int)param_1 + 0x3c)) {
    piVar5 = (int *)(*(int *)((int)param_1 + 0x44) + 0xc);
    puVar6 = puVar4 + 3;
    do {
      iVar1 = piVar5[-1];
      iVar2 = *(int *)((int)param_1 + 0xf0);
      if ((iVar1 == iVar2) && (*piVar5 == *(int *)((int)param_1 + 0xf4))) {
        if (*(int *)((int)param_1 + 0xc0) == 0) {
          *puVar6 = &LAB_005b64b0;
        }
        else {
          *puVar6 = &LAB_005b6a90;
          puVar4[2] = 1;
        }
      }
      else if (iVar1 * 2 == iVar2) {
        if (*piVar5 == *(int *)((int)param_1 + 0xf4)) {
          unaff_EDI = 0;
          *puVar6 = CDXTexture__UpsampleDispatchHorizontal;
        }
        else {
          if ((iVar1 * 2 != iVar2) || (*piVar5 * 2 - *(int *)((int)param_1 + 0xf4) != 0))
          goto LAB_005b6df4;
          if (*(int *)((int)param_1 + 0xc0) == 0) {
            *puVar6 = CDXTexture__UpsampleDispatchBilinear;
          }
          else {
            *puVar6 = &DAT_005b6800;
            puVar4[2] = 1;
          }
        }
      }
      else {
LAB_005b6df4:
        if ((iVar2 % iVar1 == 0) && (*(int *)((int)param_1 + 0xf4) % *piVar5 == 0)) {
          *puVar6 = &LAB_005b6380;
          unaff_EDI = 0;
        }
        else {
          puVar3 = *(undefined4 **)param_1;
          puVar3[5] = 0x26;
          (*(code *)*puVar3)(param_1);
        }
      }
      iVar7 = iVar7 + 1;
      puVar6 = puVar6 + 1;
      piVar5 = piVar5 + 0x15;
    } while (iVar7 < *(int *)((int)param_1 + 0x3c));
  }
  if ((*(int *)((int)param_1 + 0xc0) != 0) && (unaff_EDI == 0)) {
    iVar7 = *(int *)param_1;
    *(undefined4 *)(iVar7 + 0x14) = 99;
    (**(code **)(iVar7 + 4))(param_1,0);
  }
  return;
}
