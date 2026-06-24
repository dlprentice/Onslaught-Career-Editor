/* address: 0x005b5b80 */
/* name: CDXTexture__Helper_005b5b80 */
/* signature: void __stdcall CDXTexture__Helper_005b5b80(void * param_1) */


void CDXTexture__Helper_005b5b80(void *param_1)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  int iVar4;

  puVar3 = (undefined4 *)(*(code *)**(undefined4 **)((int)param_1 + 4))(param_1,1,0x30);
  uVar1 = *(undefined4 *)((int)param_1 + 0xc4);
  *(undefined4 **)((int)param_1 + 0x170) = puVar3;
  *puVar3 = &LAB_005b4b20;
  switch(uVar1) {
  case 0:
  case 3:
  case 5:
    puVar3[1] = &LAB_005b4ed0;
    puVar3[2] = &LAB_005be000;
    break;
  case 1:
  case 4:
  case 6:
    puVar3[1] = &LAB_005b4ed0;
    puVar3[2] = &LAB_005bdda0;
    break;
  case 2:
    puVar3[1] = &LAB_005b5370;
    puVar3[7] = &LAB_005bdb70;
    break;
  default:
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0x30;
    (*(code *)*puVar2)(param_1);
  }
  puVar3 = puVar3 + 8;
  iVar4 = 4;
  do {
    puVar3[-5] = 0;
    *puVar3 = 0;
    puVar3 = puVar3 + 1;
    iVar4 = iVar4 + -1;
  } while (iVar4 != 0);
  return;
}
