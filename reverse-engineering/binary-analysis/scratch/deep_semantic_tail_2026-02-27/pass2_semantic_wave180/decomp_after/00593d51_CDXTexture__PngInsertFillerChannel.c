/* address: 0x00593d51 */
/* name: CDXTexture__PngInsertFillerChannel */
/* signature: void __stdcall CDXTexture__PngInsertFillerChannel(void * param_1, int param_2, uint param_3, uint param_4) */


void CDXTexture__PngInsertFillerChannel(void *param_1,int param_2,uint param_3,uint param_4)

{
  uint uVar1;
  int iVar2;
  undefined1 *puVar3;
  undefined1 *puVar4;
  undefined1 uVar5;
  byte bVar6;
  uint uVar7;
  undefined1 *puVar8;

  uVar1 = *(uint *)param_1;
  bVar6 = (byte)(param_3 >> 8);
  uVar5 = (undefined1)param_3;
  if (*(char *)((int)param_1 + 8) == '\0') {
    if (*(char *)((int)param_1 + 9) == '\b') {
      puVar3 = (undefined1 *)(param_2 + uVar1);
      puVar8 = puVar3 + uVar1;
      uVar7 = uVar1;
      if ((param_4 & 0x80) == 0) {
        for (; uVar7 != 0; uVar7 = uVar7 - 1) {
          puVar3 = puVar3 + -1;
          puVar8[-1] = *puVar3;
          puVar8 = puVar8 + -2;
          *puVar8 = uVar5;
        }
      }
      else {
        if (1 < uVar1) {
          param_2 = uVar1 - 1;
          do {
            puVar3 = puVar3 + -1;
            puVar8[-1] = uVar5;
            puVar8 = puVar8 + -2;
            param_2 = param_2 + -1;
            *puVar8 = *puVar3;
          } while (param_2 != 0);
        }
        puVar8[-1] = uVar5;
      }
      *(undefined1 *)((int)param_1 + 10) = 2;
      *(undefined1 *)((int)param_1 + 0xb) = 0x10;
      iVar2 = uVar1 * 2;
    }
    else {
      if (*(char *)((int)param_1 + 9) != '\x10') {
        return;
      }
      if ((param_4 & 0x80) == 0) {
        puVar8 = (undefined1 *)(uVar1 + param_2);
        puVar3 = puVar8 + uVar1;
        for (uVar7 = uVar1; uVar7 != 0; uVar7 = uVar7 - 1) {
          puVar4 = puVar8 + -1;
          puVar8 = puVar8 + -2;
          puVar3[-1] = *puVar4;
          puVar3[-2] = *puVar8;
          puVar3[-3] = bVar6;
          puVar3 = puVar3 + -4;
          *puVar3 = uVar5;
        }
      }
      else {
        puVar8 = (undefined1 *)(param_2 + uVar1);
        puVar3 = puVar8 + uVar1;
        if (1 < uVar1) {
          param_2 = uVar1 - 1;
          uVar7 = param_3 >> 8;
          do {
            puVar3[-1] = (char)uVar7;
            puVar3[-2] = uVar5;
            puVar3[-3] = puVar8[-1];
            puVar8 = puVar8 + -2;
            puVar3 = puVar3 + -4;
            param_2 = param_2 + -1;
            *puVar3 = *puVar8;
            uVar7 = (uint)bVar6;
          } while (param_2 != 0);
        }
        puVar3[-1] = bVar6;
        puVar3[-2] = uVar5;
      }
      *(undefined1 *)((int)param_1 + 10) = 2;
      *(undefined1 *)((int)param_1 + 0xb) = 0x20;
      iVar2 = uVar1 << 2;
    }
  }
  else {
    if (*(char *)((int)param_1 + 8) != '\x02') {
      return;
    }
    if (*(char *)((int)param_1 + 9) == '\b') {
      if ((param_4 & 0x80) == 0) {
        puVar8 = (undefined1 *)(param_2 + uVar1 * 3);
        puVar3 = puVar8 + uVar1;
        for (uVar7 = uVar1; uVar7 != 0; uVar7 = uVar7 - 1) {
          puVar3[-1] = puVar8[-1];
          puVar3[-2] = puVar8[-2];
          puVar8 = puVar8 + -3;
          puVar3[-3] = *puVar8;
          puVar3 = puVar3 + -4;
          *puVar3 = uVar5;
        }
      }
      else {
        puVar8 = (undefined1 *)(param_2 + uVar1 * 3);
        puVar3 = puVar8 + uVar1;
        if (1 < uVar1) {
          param_2 = uVar1 - 1;
          do {
            puVar3[-1] = uVar5;
            puVar3[-2] = puVar8[-1];
            puVar4 = puVar8 + -2;
            puVar8 = puVar8 + -3;
            puVar3[-3] = *puVar4;
            puVar3 = puVar3 + -4;
            param_2 = param_2 + -1;
            *puVar3 = *puVar8;
          } while (param_2 != 0);
        }
        puVar3[-1] = uVar5;
      }
      *(undefined1 *)((int)param_1 + 0xb) = 0x20;
      iVar2 = 2;
    }
    else {
      if (*(char *)((int)param_1 + 9) != '\x10') {
        return;
      }
      puVar8 = (undefined1 *)(param_2 + uVar1 * 3);
      puVar3 = puVar8 + uVar1;
      uVar7 = uVar1;
      if ((param_4 & 0x80) == 0) {
        for (; uVar7 != 0; uVar7 = uVar7 - 1) {
          puVar3[-1] = puVar8[-1];
          puVar3[-2] = puVar8[-2];
          puVar3[-3] = puVar8[-3];
          puVar3[-4] = puVar8[-4];
          puVar3[-5] = puVar8[-5];
          puVar8 = puVar8 + -6;
          puVar3[-6] = *puVar8;
          puVar3[-7] = bVar6;
          puVar3 = puVar3 + -8;
          *puVar3 = uVar5;
        }
      }
      else {
        if (1 < uVar1) {
          param_2 = uVar1 - 1;
          do {
            puVar3[-1] = bVar6;
            puVar3[-2] = uVar5;
            puVar3[-3] = puVar8[-1];
            puVar3[-4] = puVar8[-2];
            puVar3[-5] = puVar8[-3];
            puVar3[-6] = puVar8[-4];
            puVar4 = puVar8 + -5;
            puVar8 = puVar8 + -6;
            puVar3[-7] = *puVar4;
            puVar3 = puVar3 + -8;
            param_2 = param_2 + -1;
            *puVar3 = *puVar8;
          } while (param_2 != 0);
        }
        puVar3[-1] = bVar6;
        puVar3[-2] = uVar5;
      }
      *(undefined1 *)((int)param_1 + 0xb) = 0x40;
      iVar2 = 3;
    }
    iVar2 = uVar1 << iVar2;
    *(undefined1 *)((int)param_1 + 10) = 4;
  }
  *(int *)((int)param_1 + 4) = iVar2;
  return;
}
