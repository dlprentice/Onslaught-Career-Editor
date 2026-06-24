/* address: 0x005b7580 */
/* name: CDXTexture__InitColorConverterDispatch */
/* signature: void __stdcall CDXTexture__InitColorConverterDispatch(void * param_1) */


void CDXTexture__InitColorConverterDispatch(void *param_1)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 *puVar4;
  bool bVar5;

  puVar4 = (undefined4 *)(*(code *)**(undefined4 **)((int)param_1 + 4))(param_1,1,0xc);
  uVar1 = *(undefined4 *)((int)param_1 + 0x28);
  *(undefined4 **)((int)param_1 + 0x168) = puVar4;
  *puVar4 = &DAT_005b0ed0;
  switch(uVar1) {
  case 1:
    if (*(int *)((int)param_1 + 0x24) != 1) {
LAB_005b75d0:
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 9;
      (*(code *)*puVar2)(param_1);
    }
    break;
  case 2:
  case 3:
    if (*(int *)((int)param_1 + 0x24) != 3) goto LAB_005b75d0;
    break;
  case 4:
  case 5:
    if (*(int *)((int)param_1 + 0x24) != 4) goto LAB_005b75d0;
    break;
  default:
    if (*(int *)((int)param_1 + 0x24) < 1) goto LAB_005b75d0;
  }
  switch(*(int *)((int)param_1 + 0x40)) {
  case 1:
    if (*(int *)((int)param_1 + 0x3c) != 1) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 10;
      (*(code *)*puVar2)(param_1);
    }
    iVar3 = *(int *)((int)param_1 + 0x28);
    if (iVar3 == 1) {
LAB_005b7649:
      puVar4[1] = CDXTexture__CopyInterleavedChannelRows;
      return;
    }
    if (iVar3 == 2) {
      *puVar4 = &LAB_005b6e70;
      puVar4[1] = CDXTexture__ConvertRgbRowsToGrayscale;
      return;
    }
    if ((iVar3 == 6) || (iVar3 == 7)) {
      *puVar4 = &LAB_005b6e70;
      puVar4[1] = &LAB_005b7250;
      return;
    }
    if (iVar3 == 3) goto LAB_005b7649;
    goto LAB_005b7706;
  case 2:
    if (*(int *)((int)param_1 + 0x3c) != 3) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 10;
      (*(code *)*puVar2)(param_1);
    }
    bVar5 = *(int *)((int)param_1 + 0x28) == 2;
    break;
  case 3:
    if (*(int *)((int)param_1 + 0x3c) != 3) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 10;
      (*(code *)*puVar2)(param_1);
    }
    iVar3 = *(int *)((int)param_1 + 0x28);
    if (iVar3 == 2) {
      *puVar4 = &LAB_005b6e70;
      puVar4[1] = &LAB_005b6f50;
      return;
    }
    if ((iVar3 == 6) || (iVar3 == 7)) {
      *puVar4 = &LAB_005b6e70;
      puVar4[1] = &LAB_005b7080;
      return;
    }
    bVar5 = iVar3 == 3;
    break;
  case 4:
    if (*(int *)((int)param_1 + 0x3c) != 4) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 10;
      (*(code *)*puVar2)(param_1);
    }
    bVar5 = *(int *)((int)param_1 + 0x28) == 4;
    break;
  case 5:
    if (*(int *)((int)param_1 + 0x3c) != 4) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 10;
      (*(code *)*puVar2)(param_1);
    }
    if (*(int *)((int)param_1 + 0x28) == 4) {
      *puVar4 = &LAB_005b6e70;
      puVar4[1] = &LAB_005b7300;
      return;
    }
    bVar5 = *(int *)((int)param_1 + 0x28) == 5;
    break;
  default:
    if ((*(int *)((int)param_1 + 0x40) != *(int *)((int)param_1 + 0x28)) ||
       (*(int *)((int)param_1 + 0x3c) != *(int *)((int)param_1 + 0x24))) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 0x1b;
      (*(code *)*puVar2)(param_1);
    }
    goto LAB_005b7731;
  }
  if (bVar5) {
LAB_005b7731:
    puVar4[1] = &LAB_005b74e0;
    return;
  }
LAB_005b7706:
  puVar4 = *(undefined4 **)param_1;
  puVar4[5] = 0x1b;
  (*(code *)*puVar4)(param_1);
  return;
}
