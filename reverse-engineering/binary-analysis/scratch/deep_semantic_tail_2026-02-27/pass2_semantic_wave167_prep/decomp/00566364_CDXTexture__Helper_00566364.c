/* address: 0x00566364 */
/* name: CDXTexture__Helper_00566364 */
/* signature: void __cdecl CDXTexture__Helper_00566364(void * param_1, int param_2) */


void __cdecl CDXTexture__Helper_00566364(void *param_1,int param_2)

{
  char *pcVar1;
  uint *puVar2;
  int *piVar3;
  char cVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  byte bVar8;
  uint uVar9;
  void *pvVar10;
  void *pvVar11;
  uint *puVar12;
  uint uVar13;
  uint uVar14;
  uint local_8;

  iVar5 = *(int *)((int)param_1 + 0x10);
  puVar12 = (uint *)(param_2 + -4);
  uVar14 = (uint)(param_2 - *(int *)((int)param_1 + 0xc)) >> 0xf;
  piVar3 = (int *)(uVar14 * 0x204 + 0x144 + iVar5);
  uVar13 = *puVar12;
  local_8 = uVar13 - 1;
  if ((local_8 & 1) == 0) {
    uVar6 = *(uint *)(local_8 + (int)puVar12);
    uVar7 = *(uint *)(param_2 + -8);
    if ((uVar6 & 1) == 0) {
      uVar9 = ((int)uVar6 >> 4) - 1;
      if (0x3f < uVar9) {
        uVar9 = 0x3f;
      }
      if (*(int *)((int)puVar12 + uVar13 + 3) == *(int *)((int)puVar12 + uVar13 + 7)) {
        if (uVar9 < 0x20) {
          pcVar1 = (char *)(uVar9 + 4 + iVar5);
          uVar9 = ~(0x80000000U >> ((byte)uVar9 & 0x1f));
          puVar2 = (uint *)(iVar5 + 0x44 + uVar14 * 4);
          *puVar2 = *puVar2 & uVar9;
          *pcVar1 = *pcVar1 + -1;
          if (*pcVar1 == '\0') {
            *(uint *)param_1 = *(uint *)param_1 & uVar9;
          }
        }
        else {
          pcVar1 = (char *)(uVar9 + 4 + iVar5);
          uVar9 = ~(0x80000000U >> ((byte)uVar9 - 0x20 & 0x1f));
          puVar2 = (uint *)(iVar5 + 0xc4 + uVar14 * 4);
          *puVar2 = *puVar2 & uVar9;
          *pcVar1 = *pcVar1 + -1;
          if (*pcVar1 == '\0') {
            *(uint *)((int)param_1 + 4) = *(uint *)((int)param_1 + 4) & uVar9;
          }
        }
      }
      local_8 = local_8 + uVar6;
      *(undefined4 *)(*(int *)((int)puVar12 + uVar13 + 7) + 4) =
           *(undefined4 *)((int)puVar12 + uVar13 + 3);
      *(undefined4 *)(*(int *)((int)puVar12 + uVar13 + 3) + 8) =
           *(undefined4 *)((int)puVar12 + uVar13 + 7);
    }
    pvVar10 = (void *)(((int)local_8 >> 4) - 1);
    if ((void *)0x3f < pvVar10) {
      pvVar10 = (void *)0x3f;
    }
    pvVar11 = param_1;
    if ((uVar7 & 1) == 0) {
      puVar12 = (uint *)((int)puVar12 - uVar7);
      pvVar11 = (void *)(((int)uVar7 >> 4) - 1);
      if ((void *)0x3f < pvVar11) {
        pvVar11 = (void *)0x3f;
      }
      local_8 = local_8 + uVar7;
      pvVar10 = (void *)(((int)local_8 >> 4) - 1);
      if ((void *)0x3f < pvVar10) {
        pvVar10 = (void *)0x3f;
      }
      if (pvVar11 != pvVar10) {
        if (puVar12[1] == puVar12[2]) {
          if (pvVar11 < (void *)0x20) {
            uVar13 = ~(0x80000000U >> ((byte)pvVar11 & 0x1f));
            puVar2 = (uint *)(iVar5 + 0x44 + uVar14 * 4);
            *puVar2 = *puVar2 & uVar13;
            pcVar1 = (char *)((int)pvVar11 + iVar5 + 4);
            *pcVar1 = *pcVar1 + -1;
            if (*pcVar1 == '\0') {
              *(uint *)param_1 = *(uint *)param_1 & uVar13;
            }
          }
          else {
            uVar13 = ~(0x80000000U >> ((byte)pvVar11 - 0x20 & 0x1f));
            puVar2 = (uint *)(iVar5 + 0xc4 + uVar14 * 4);
            *puVar2 = *puVar2 & uVar13;
            pcVar1 = (char *)((int)pvVar11 + iVar5 + 4);
            *pcVar1 = *pcVar1 + -1;
            if (*pcVar1 == '\0') {
              *(uint *)((int)param_1 + 4) = *(uint *)((int)param_1 + 4) & uVar13;
            }
          }
        }
        *(uint *)(puVar12[2] + 4) = puVar12[1];
        *(uint *)(puVar12[1] + 8) = puVar12[2];
      }
    }
    if (((uVar7 & 1) != 0) || (pvVar11 != pvVar10)) {
      puVar12[1] = piVar3[(int)pvVar10 * 2 + 1];
      puVar12[2] = (uint)(piVar3 + (int)pvVar10 * 2);
      (piVar3 + (int)pvVar10 * 2)[1] = (int)puVar12;
      *(uint **)(puVar12[1] + 8) = puVar12;
      if (puVar12[1] == puVar12[2]) {
        cVar4 = *(char *)((int)pvVar10 + iVar5 + 4);
        *(char *)((int)pvVar10 + iVar5 + 4) = cVar4 + '\x01';
        bVar8 = (byte)pvVar10;
        if (pvVar10 < (void *)0x20) {
          if (cVar4 == '\0') {
            *(uint *)param_1 = *(uint *)param_1 | 0x80000000U >> (bVar8 & 0x1f);
          }
          puVar2 = (uint *)(iVar5 + 0x44 + uVar14 * 4);
          *puVar2 = *puVar2 | 0x80000000U >> (bVar8 & 0x1f);
        }
        else {
          if (cVar4 == '\0') {
            *(uint *)((int)param_1 + 4) =
                 *(uint *)((int)param_1 + 4) | 0x80000000U >> (bVar8 - 0x20 & 0x1f);
          }
          puVar2 = (uint *)(iVar5 + 0xc4 + uVar14 * 4);
          *puVar2 = *puVar2 | 0x80000000U >> (bVar8 - 0x20 & 0x1f);
        }
      }
    }
    *puVar12 = local_8;
    *(uint *)((local_8 - 4) + (int)puVar12) = local_8;
    *piVar3 = *piVar3 + -1;
    if (*piVar3 == 0) {
      if (DAT_009d35d4 != (void *)0x0) {
        VirtualFree((LPVOID)(DAT_009d35cc * 0x8000 + *(int *)((int)DAT_009d35d4 + 0xc)),0x8000,
                    0x4000);
        *(uint *)((int)DAT_009d35d4 + 8) =
             *(uint *)((int)DAT_009d35d4 + 8) | 0x80000000U >> ((byte)DAT_009d35cc & 0x1f);
        *(undefined4 *)(*(int *)((int)DAT_009d35d4 + 0x10) + 0xc4 + DAT_009d35cc * 4) = 0;
        pcVar1 = (char *)(*(int *)((int)DAT_009d35d4 + 0x10) + 0x43);
        *pcVar1 = *pcVar1 + -1;
        if (*(char *)(*(int *)((int)DAT_009d35d4 + 0x10) + 0x43) == '\0') {
          *(uint *)((int)DAT_009d35d4 + 4) = *(uint *)((int)DAT_009d35d4 + 4) & 0xfffffffe;
        }
        if (*(int *)((int)DAT_009d35d4 + 8) == -1) {
          VirtualFree(*(LPVOID *)((int)DAT_009d35d4 + 0xc),0,0x8000);
          HeapFree(DAT_009d35e4,0,*(LPVOID *)((int)DAT_009d35d4 + 0x10));
          CRT__MemMoveOverlapSafe
                    (DAT_009d35d4,(void *)((int)DAT_009d35d4 + 0x14),
                     (DAT_009d35d8 * 0x14 - (int)DAT_009d35d4) + -0x14 + DAT_009d35dc);
          DAT_009d35d8 = DAT_009d35d8 + -1;
          if (DAT_009d35d4 < param_1) {
            param_1 = (void *)((int)param_1 + -0x14);
          }
          DAT_009d35d0 = DAT_009d35dc;
        }
      }
      DAT_009d35d4 = param_1;
      DAT_009d35cc = uVar14;
    }
  }
  return;
}
