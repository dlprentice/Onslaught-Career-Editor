/* address: 0x005b0ee0 */
/* name: CTexture__Helper_005b0ee0 */
/* signature: void __stdcall CTexture__Helper_005b0ee0(void * param_1) */


void CTexture__Helper_005b0ee0(void *param_1)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  int iVar4;

  puVar3 = (undefined4 *)(*(code *)**(undefined4 **)((int)param_1 + 4))(param_1,1,0x40);
  uVar1 = *(undefined4 *)((int)param_1 + 0x28);
  *(undefined4 **)((int)param_1 + 0x1cc) = puVar3;
  *puVar3 = &DAT_005b0ed0;
  switch(uVar1) {
  case 1:
    if (*(int *)((int)param_1 + 0x24) != 1) {
LAB_005b0f2c:
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 10;
      (*(code *)*puVar2)(param_1);
    }
    break;
  case 2:
  case 3:
    if (*(int *)((int)param_1 + 0x24) != 3) goto LAB_005b0f2c;
    break;
  case 4:
  case 5:
    if (*(int *)((int)param_1 + 0x24) != 4) goto LAB_005b0f2c;
    break;
  default:
    if (*(int *)((int)param_1 + 0x24) < 1) goto LAB_005b0f2c;
  }
  iVar4 = *(int *)((int)param_1 + 0x2c);
  if (iVar4 == 1) {
    *(undefined4 *)((int)param_1 + 0x78) = 1;
    if ((*(int *)((int)param_1 + 0x28) == 1) || (*(int *)((int)param_1 + 0x28) == 3)) {
      iVar4 = *(int *)((int)param_1 + 0x24);
      puVar3[1] = &LAB_005afc60;
      if (1 < iVar4) {
        puVar3 = (undefined4 *)(*(int *)((int)param_1 + 0xdc) + 0x84);
        iVar4 = *(int *)((int)param_1 + 0x24) + -1;
        do {
          *puVar3 = 0;
          puVar3 = puVar3 + 0x15;
          iVar4 = iVar4 + -1;
        } while (iVar4 != 0);
      }
      goto LAB_005b107c;
    }
  }
  else if (iVar4 == 2) {
    iVar4 = *(int *)((int)param_1 + 0x28);
    *(undefined4 *)((int)param_1 + 0x78) = 3;
    if (iVar4 == 3) {
      if ((*(int *)((int)param_1 + 0x48) == 5) || (*(int *)((int)param_1 + 0x48) == 6)) {
        puVar3[1] = &LAB_005afa60;
        CTexture__Helper_005af860();
      }
      else {
        puVar3[1] = &LAB_005af930;
        CTexture__Helper_005af860();
      }
      goto LAB_005b107c;
    }
    if (iVar4 == 1) {
      puVar3[1] = &LAB_005afc90;
      goto LAB_005b107c;
    }
    if (iVar4 == 2) {
      puVar3[1] = CTexture__Helper_005afbd0;
      goto LAB_005b107c;
    }
    if (iVar4 == 4) {
      puVar3[1] = &LAB_005b0ac0;
      CDXTexture__Helper_005afe60();
      goto LAB_005b107c;
    }
    if (iVar4 == 5) {
      puVar3[1] = &LAB_005b0ca0;
      CTexture__Helper_005af860();
      CDXTexture__Helper_005afe60();
      goto LAB_005b107c;
    }
  }
  else if (iVar4 == 4) {
    *(undefined4 *)((int)param_1 + 0x78) = 4;
    if (*(int *)((int)param_1 + 0x28) == 5) {
      puVar3[1] = CDXTexture__Helper_005afcf0;
      CTexture__Helper_005af860();
      goto LAB_005b107c;
    }
    if (*(int *)((int)param_1 + 0x28) == 4) {
      puVar3[1] = CTexture__Helper_005afbd0;
      goto LAB_005b107c;
    }
  }
  else if (iVar4 == *(int *)((int)param_1 + 0x28)) {
    *(undefined4 *)((int)param_1 + 0x78) = *(undefined4 *)((int)param_1 + 0x24);
    puVar3[1] = CTexture__Helper_005afbd0;
    goto LAB_005b107c;
  }
  puVar3 = *(undefined4 **)param_1;
  puVar3[5] = 0x1b;
  (*(code *)*puVar3)(param_1);
LAB_005b107c:
  if (*(int *)((int)param_1 + 0x54) == 0) {
    *(undefined4 *)((int)param_1 + 0x7c) = *(undefined4 *)((int)param_1 + 0x78);
    return;
  }
  *(undefined4 *)((int)param_1 + 0x7c) = 1;
  return;
}
