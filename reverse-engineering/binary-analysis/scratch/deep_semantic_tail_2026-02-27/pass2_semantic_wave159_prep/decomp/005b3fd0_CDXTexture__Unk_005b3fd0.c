/* address: 0x005b3fd0 */
/* name: CDXTexture__Unk_005b3fd0 */
/* signature: void CDXTexture__Unk_005b3fd0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__Unk_005b3fd0(void)

{
  int *piVar1;
  undefined4 *puVar2;
  int in_EAX;
  int iVar3;
  int iVar4;
  char *pcVar5;

  if (*(int *)(in_EAX + 0x38) != 0) {
    iVar3 = *(int *)(in_EAX + 0x38) >> 1;
    iVar4 = 0;
    if (iVar3 != 0) {
      do {
        iVar3 = iVar3 >> 1;
        iVar4 = iVar4 + 1;
      } while (iVar3 != 0);
      if (0xe < iVar4) {
        piVar1 = *(int **)(in_EAX + 0x20);
        puVar2 = (undefined4 *)*piVar1;
        puVar2[5] = 0x28;
        (*(code *)*puVar2)(piVar1);
      }
    }
    if (*(int *)(in_EAX + 0xc) == 0) {
      CDXTexture__Helper_005b3ec0
                (*(uint *)(*(int *)(in_EAX + 0x4c + *(int *)(in_EAX + 0x34) * 4) + iVar4 * 0x40));
    }
    else {
      piVar1 = (int *)(*(int *)(in_EAX + 0x5c + *(int *)(in_EAX + 0x34) * 4) + iVar4 * 0x40);
      *piVar1 = *piVar1 + 1;
    }
    if (iVar4 != 0) {
      CDXTexture__Helper_005b3ec0(*(uint *)(in_EAX + 0x38));
    }
    iVar3 = *(int *)(in_EAX + 0x3c);
    pcVar5 = *(char **)(in_EAX + 0x40);
    *(undefined4 *)(in_EAX + 0x38) = 0;
    if (*(int *)(in_EAX + 0xc) == 0) {
      for (; iVar3 != 0; iVar3 = iVar3 + -1) {
        CDXTexture__Helper_005b3ec0((int)*pcVar5);
        pcVar5 = pcVar5 + 1;
      }
    }
    *(undefined4 *)(in_EAX + 0x3c) = 0;
  }
  return;
}
