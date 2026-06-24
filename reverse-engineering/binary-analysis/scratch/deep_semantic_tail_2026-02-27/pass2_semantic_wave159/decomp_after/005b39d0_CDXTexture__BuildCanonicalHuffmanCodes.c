/* address: 0x005b39d0 */
/* name: CDXTexture__BuildCanonicalHuffmanCodes */
/* signature: void __stdcall CDXTexture__BuildCanonicalHuffmanCodes(void * param_1, void * param_2, int param_3) */


void CDXTexture__BuildCanonicalHuffmanCodes(void *param_1,void *param_2,int param_3)

{
  char *pcVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 *puVar8;
  int *piVar9;
  undefined4 local_82c;
  undefined4 uStack_828;
  undefined4 uStack_824;
  undefined4 uStack_820;
  char cStack_81c;
  int local_808 [257];
  int local_404 [257];

  puVar8 = &local_82c;
  for (iVar4 = 8; iVar4 != 0; iVar4 = iVar4 + -1) {
    *puVar8 = 0;
    puVar8 = puVar8 + 1;
  }
  *(undefined1 *)puVar8 = 0;
  piVar9 = local_808;
  for (iVar4 = 0x101; iVar4 != 0; iVar4 = iVar4 + -1) {
    *piVar9 = 0;
    piVar9 = piVar9 + 1;
  }
  piVar9 = local_404;
  for (iVar4 = 0x101; iVar4 != 0; iVar4 = iVar4 + -1) {
    *piVar9 = -1;
    piVar9 = piVar9 + 1;
  }
  *(undefined4 *)(param_3 + 0x400) = 1;
  while( true ) {
    iVar4 = -1;
    iVar7 = 1000000000;
    iVar5 = 0;
    do {
      iVar6 = *(int *)(param_3 + iVar5 * 4);
      if ((iVar6 != 0) && (iVar6 <= iVar7)) {
        iVar4 = iVar5;
        iVar7 = iVar6;
      }
      iVar5 = iVar5 + 1;
    } while (iVar5 < 0x101);
    iVar7 = -1;
    iVar5 = 1000000000;
    iVar6 = 0;
    do {
      iVar3 = *(int *)(param_3 + iVar6 * 4);
      if (((iVar3 != 0) && (iVar3 <= iVar5)) && (iVar6 != iVar4)) {
        iVar7 = iVar6;
        iVar5 = iVar3;
      }
      iVar6 = iVar6 + 1;
    } while (iVar6 < 0x101);
    if (iVar7 < 0) break;
    iVar5 = local_808[iVar4];
    *(int *)(param_3 + iVar4 * 4) = *(int *)(param_3 + iVar4 * 4) + *(int *)(param_3 + iVar7 * 4);
    iVar6 = local_404[iVar4];
    piVar9 = local_404 + iVar4;
    *(undefined4 *)(param_3 + iVar7 * 4) = 0;
    local_808[iVar4] = iVar5 + 1;
    while (-1 < iVar6) {
      iVar4 = *piVar9;
      iVar6 = local_404[iVar4];
      piVar9 = local_404 + iVar4;
      local_808[iVar4] = local_808[iVar4] + 1;
    }
    iVar5 = local_808[iVar7];
    local_404[iVar4] = iVar7;
    iVar4 = local_404[iVar7];
    piVar9 = local_404 + iVar7;
    local_808[iVar7] = iVar5 + 1;
    while (-1 < iVar4) {
      iVar7 = *piVar9;
      iVar4 = local_404[iVar7];
      local_808[iVar7] = local_808[iVar7] + 1;
      piVar9 = local_404 + iVar7;
    }
  }
  iVar4 = 0;
  do {
    iVar7 = local_808[iVar4];
    if (iVar7 != 0) {
      if (0x20 < iVar7) {
        puVar8 = *(undefined4 **)param_1;
        puVar8[5] = 0x27;
        (*(code *)*puVar8)(param_1);
      }
      *(char *)((int)&local_82c + iVar7) = *(char *)((int)&local_82c + iVar7) + '\x01';
    }
    iVar4 = iVar4 + 1;
  } while (iVar4 < 0x101);
  iVar5 = 0x10;
  iVar7 = 0x1e;
  iVar4 = 0x10;
  do {
    cVar2 = *(char *)((int)&local_82c + iVar7 + 2);
    while (cVar2 != '\0') {
      cVar2 = *(char *)((int)&local_82c + iVar7);
      iVar6 = iVar7;
      while (cVar2 == '\0') {
        pcVar1 = &stack0xfffff7d3 + iVar6;
        iVar6 = iVar6 + -1;
        cVar2 = *pcVar1;
      }
      pcVar1 = (char *)((int)&local_82c + iVar7 + 2);
      *pcVar1 = *pcVar1 + -2;
      pcVar1 = (char *)((int)&local_82c + iVar7 + 1);
      *pcVar1 = *pcVar1 + '\x01';
      pcVar1 = (char *)((int)&local_82c + iVar6 + 1);
      *pcVar1 = *pcVar1 + '\x02';
      *(char *)((int)&local_82c + iVar6) = *(char *)((int)&local_82c + iVar6) + -1;
      cVar2 = *(char *)((int)&local_82c + iVar7 + 2);
    }
    iVar7 = iVar7 + -1;
    iVar5 = iVar5 + -1;
    cVar2 = cStack_81c;
  } while (iVar5 != 0);
  while (cVar2 == '\0') {
    pcVar1 = &stack0xfffff7d3 + iVar4;
    iVar4 = iVar4 + -1;
    cVar2 = *pcVar1;
  }
  *(char *)((int)&local_82c + iVar4) = *(char *)((int)&local_82c + iVar4) + -1;
  *(undefined4 *)param_2 = local_82c;
  *(undefined4 *)((int)param_2 + 4) = uStack_828;
  *(undefined4 *)((int)param_2 + 8) = uStack_824;
  *(undefined4 *)((int)param_2 + 0xc) = uStack_820;
  *(char *)((int)param_2 + 0x10) = cStack_81c;
  iVar4 = 0;
  iVar7 = 1;
  do {
    iVar5 = 0;
    do {
      if (local_808[iVar5] == iVar7) {
        *(char *)(iVar4 + 0x11 + (int)param_2) = (char)iVar5;
        iVar4 = iVar4 + 1;
      }
      iVar5 = iVar5 + 1;
    } while (iVar5 < 0x100);
    iVar7 = iVar7 + 1;
  } while (iVar7 < 0x21);
  *(undefined4 *)((int)param_2 + 0x114) = 0;
  return;
}
