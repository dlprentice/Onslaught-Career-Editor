/* address: 0x00567130 */
/* name: CTexture__Unk_00567130 */
/* signature: int * __cdecl CTexture__Unk_00567130(uint param_1) */


/* WARNING: Type propagation algorithm not settling */

int * __cdecl CTexture__Unk_00567130(uint param_1)

{
  uint *puVar1;
  undefined **ppuVar2;
  void *pvVar3;
  int *piVar4;
  undefined *puVar5;
  undefined **ppuVar6;
  int *piVar7;
  uint *puVar8;
  undefined **ppuVar9;
  int local_8;

  piVar7 = (int *)PTR_LOOP_00655da0;
  do {
    if (piVar7[4] != -1) {
      puVar8 = (uint *)piVar7[2];
      pvVar3 = (void *)(((int)puVar8 + (-0x18 - (int)piVar7) >> 3) * 0x1000 + piVar7[4]);
      if (puVar8 < piVar7 + 0x806) {
        do {
          if (((int)param_1 <= (int)*puVar8) && (param_1 < puVar8[1])) {
            piVar4 = (int *)CTexture__Helper_00567338(pvVar3,*puVar8,param_1);
            if (piVar4 != (int *)0x0) goto LAB_005671fb;
            puVar8[1] = param_1;
          }
          puVar8 = puVar8 + 2;
          pvVar3 = (void *)((int)pvVar3 + 0x1000);
        } while (puVar8 < piVar7 + 0x806);
      }
      puVar1 = (uint *)piVar7[2];
      pvVar3 = (void *)piVar7[4];
      for (puVar8 = (uint *)(piVar7 + 6); puVar8 < puVar1; puVar8 = puVar8 + 2) {
        if (((int)param_1 <= (int)*puVar8) && (param_1 < puVar8[1])) {
          piVar4 = (int *)CTexture__Helper_00567338(pvVar3,*puVar8,param_1);
          if (piVar4 != (int *)0x0) {
LAB_005671fb:
            PTR_LOOP_00655da0 = (undefined *)piVar7;
            *puVar8 = *puVar8 - param_1;
            piVar7[2] = (int)puVar8;
            return piVar4;
          }
          puVar8[1] = param_1;
        }
        pvVar3 = (void *)((int)pvVar3 + 0x1000);
      }
    }
    piVar7 = (int *)*piVar7;
    if (piVar7 == (int *)PTR_LOOP_00655da0) {
      ppuVar9 = &PTR_LOOP_00653d80;
      while ((ppuVar9[4] == (undefined *)0xffffffff || (ppuVar9[3] == (undefined *)0x0))) {
        ppuVar9 = (undefined **)*ppuVar9;
        if (ppuVar9 == &PTR_LOOP_00653d80) {
          puVar5 = (undefined *)CTexture__Unk_00566e38();
          if (puVar5 == (undefined *)0x0) {
            return (int *)0x0;
          }
          piVar7 = *(int **)(puVar5 + 0x10);
          *(char *)(piVar7 + 2) = (char)param_1;
          PTR_LOOP_00655da0 = puVar5;
          *piVar7 = (int)piVar7 + param_1 + 8;
          piVar7[1] = 0xf0 - param_1;
          *(uint *)(puVar5 + 0x18) = *(int *)(puVar5 + 0x18) - (param_1 & 0xff);
          return piVar7 + 0x40;
        }
      }
      ppuVar2 = (undefined **)ppuVar9[3];
      local_8 = 0;
      piVar7 = (int *)(ppuVar9[4] + ((int)ppuVar2 + (-0x18 - (int)ppuVar9) >> 3) * 0x1000);
      puVar5 = *ppuVar2;
      ppuVar6 = ppuVar2;
      for (; (puVar5 == (undefined *)0xffffffff && (local_8 < 0x10)); local_8 = local_8 + 1) {
        ppuVar6 = ppuVar6 + 2;
        puVar5 = *ppuVar6;
      }
      piVar4 = VirtualAlloc(piVar7,local_8 << 0xc,0x1000,4);
      if (piVar4 != piVar7) {
        return (int *)0x0;
      }
      _memset(piVar7,local_8 << 0xc,0);
      ppuVar6 = ppuVar2;
      if (0 < local_8) {
        piVar4 = piVar7 + 1;
        do {
          *(undefined1 *)(piVar4 + 0x3d) = 0xff;
          piVar4[-1] = (int)(piVar4 + 1);
          *piVar4 = 0xf0;
          *ppuVar6 = (undefined *)0xf0;
          ppuVar6[1] = (undefined *)0xf1;
          piVar4 = piVar4 + 0x400;
          ppuVar6 = ppuVar6 + 2;
          local_8 = local_8 + -1;
        } while (local_8 != 0);
      }
      for (; (ppuVar6 < ppuVar9 + 0x806 && (*ppuVar6 != (undefined *)0xffffffff));
          ppuVar6 = ppuVar6 + 2) {
      }
      PTR_LOOP_00655da0 = (undefined *)ppuVar9;
      ppuVar9[3] = (undefined *)(-(uint)(ppuVar6 < ppuVar9 + 0x806) & (uint)ppuVar6);
      *(char *)(piVar7 + 2) = (char)param_1;
      ppuVar9[2] = (undefined *)ppuVar2;
      *ppuVar2 = *ppuVar2 + -param_1;
      piVar7[1] = piVar7[1] - param_1;
      *piVar7 = (int)piVar7 + param_1 + 8;
      return piVar7 + 0x40;
    }
  } while( true );
}
