/* address: 0x00593f8a */
/* name: CFastVB__Helper_00593f8a */
/* signature: void __stdcall CFastVB__Helper_00593f8a(void * param_1, void * param_2, int param_3, void * param_4, int param_5) */


void CFastVB__Helper_00593f8a(void *param_1,void *param_2,int param_3,void *param_4,int param_5)

{
  byte bVar1;
  char cVar2;
  undefined2 uVar3;
  int iVar4;
  void *pvVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  int iVar10;

  pvVar5 = param_4;
  iVar4 = param_3;
  bVar1 = *(byte *)((int)param_1 + 9);
  iVar10 = *(int *)param_1;
  if (((bVar1 < 9) && (param_3 != 0)) || ((bVar1 == 0x10 && (param_4 != (void *)0x0)))) {
    cVar2 = *(char *)((int)param_1 + 8);
    if (cVar2 == '\0') {
      if ((bVar1 == 2) && (param_4 = param_2, iVar10 != 0)) {
        param_3 = (iVar10 - 1U >> 2) + 1;
        do {
          uVar6 = (uint)*(byte *)param_4;
          uVar8 = uVar6 & 0xc0;
          uVar7 = uVar6 & 3;
          uVar9 = uVar6 & 0xc;
          uVar6 = uVar6 & 0x30;
          param_3 = param_3 + -1;
          *(byte *)param_4 =
               (byte)((byte)(*(byte *)(((uVar9 << 2 | uVar9) << 2 | (int)uVar9 >> 2 | uVar9) + iVar4
                                      ) & 0xcf |
                            *(byte *)((((uVar7 << 2 | uVar7) << 2 | uVar7) << 2 | uVar7) + iVar4) >>
                            2) >> 2 |
                     *(byte *)(((int)((int)uVar6 >> 2 | uVar6) >> 2 | uVar6 << 2 | uVar6) + iVar4) &
                     0xc3) >> 2 |
               *(byte *)(((int)((int)((int)uVar8 >> 2 | uVar8) >> 2 | uVar8) >> 2 | uVar8) + iVar4)
               & 0xc0;
          param_4 = (void *)((int)param_4 + 1);
        } while (param_3 != 0);
      }
      cVar2 = *(char *)((int)param_1 + 9);
      if (cVar2 == '\x04') {
        if (iVar10 != 0) {
          iVar10 = (iVar10 - 1U >> 1) + 1;
          do {
            uVar7 = *(byte *)param_2 & 0xf0;
            uVar6 = *(byte *)param_2 & 0xf;
            *(byte *)param_2 =
                 *(byte *)(((int)uVar7 >> 4 | uVar7) + iVar4) & 0xf0 |
                 *(byte *)((uVar6 << 4 | uVar6) + iVar4) >> 4;
            param_2 = (void *)((int)param_2 + 1);
            iVar10 = iVar10 + -1;
          } while (iVar10 != 0);
        }
      }
      else if (cVar2 == '\b') {
        for (; iVar10 != 0; iVar10 = iVar10 + -1) {
          *(byte *)param_2 = *(byte *)((uint)*(byte *)param_2 + iVar4);
          param_2 = (void *)((int)param_2 + 1);
        }
      }
      else if (cVar2 == '\x10') {
        for (; iVar10 != 0; iVar10 = iVar10 + -1) {
          uVar3 = *(undefined2 *)
                   (*(int *)((int)pvVar5 +
                            (uint)(*(byte *)((int)param_2 + 1) >> ((byte)param_5 & 0x1f)) * 4) +
                   (uint)*(byte *)param_2 * 2);
          *(byte *)param_2 = (byte)((ushort)uVar3 >> 8);
          *(byte *)((int)param_2 + 1) = (byte)uVar3;
          param_2 = (void *)((int)param_2 + 2);
        }
      }
    }
    else if (cVar2 == '\x02') {
      if (bVar1 == 8) {
        for (; iVar10 != 0; iVar10 = iVar10 + -1) {
          *(byte *)param_2 = *(byte *)((uint)*(byte *)param_2 + param_3);
          *(byte *)((int)param_2 + 1) = *(byte *)((uint)*(byte *)((int)param_2 + 1) + param_3);
          *(byte *)((int)param_2 + 2) = *(byte *)((uint)*(byte *)((int)param_2 + 2) + param_3);
          param_2 = (void *)((int)param_2 + 3);
        }
      }
      else {
        for (; iVar10 != 0; iVar10 = iVar10 + -1) {
          uVar3 = *(undefined2 *)
                   (*(int *)((int)param_4 +
                            (uint)(*(byte *)((int)param_2 + 1) >> ((byte)param_5 & 0x1f)) * 4) +
                   (uint)*(byte *)param_2 * 2);
          *(byte *)((int)param_2 + 1) = (byte)uVar3;
          *(byte *)param_2 = (byte)((ushort)uVar3 >> 8);
          uVar3 = *(undefined2 *)
                   (*(int *)((int)param_4 +
                            (uint)(*(byte *)((int)param_2 + 3) >> ((byte)param_5 & 0x1f)) * 4) +
                   (uint)*(byte *)((int)param_2 + 2) * 2);
          *(byte *)((int)param_2 + 3) = (byte)uVar3;
          *(byte *)((int)param_2 + 2) = (byte)((ushort)uVar3 >> 8);
          uVar3 = *(undefined2 *)
                   (*(int *)((int)param_4 +
                            (uint)(*(byte *)((int)param_2 + 5) >> ((byte)param_5 & 0x1f)) * 4) +
                   (uint)*(byte *)((int)param_2 + 4) * 2);
          *(byte *)((int)param_2 + 4) = (byte)((ushort)uVar3 >> 8);
          *(byte *)((int)param_2 + 5) = (byte)uVar3;
          param_2 = (void *)((int)param_2 + 6);
        }
      }
    }
    else if (cVar2 == '\x04') {
      if (bVar1 == 8) {
        for (; iVar10 != 0; iVar10 = iVar10 + -1) {
          *(byte *)param_2 = *(byte *)((uint)*(byte *)param_2 + param_3);
          param_2 = (void *)((int)param_2 + 2);
        }
      }
      else {
        for (; iVar10 != 0; iVar10 = iVar10 + -1) {
          uVar3 = *(undefined2 *)
                   (*(int *)((int)param_4 +
                            (uint)(*(byte *)((int)param_2 + 1) >> ((byte)param_5 & 0x1f)) * 4) +
                   (uint)*(byte *)param_2 * 2);
          *(byte *)param_2 = (byte)((ushort)uVar3 >> 8);
          *(byte *)((int)param_2 + 1) = (byte)uVar3;
          param_2 = (void *)((int)param_2 + 4);
        }
      }
    }
    else if (cVar2 == '\x06') {
      if (bVar1 == 8) {
        for (; iVar10 != 0; iVar10 = iVar10 + -1) {
          *(byte *)param_2 = *(byte *)((uint)*(byte *)param_2 + param_3);
          *(byte *)((int)param_2 + 1) = *(byte *)((uint)*(byte *)((int)param_2 + 1) + param_3);
          *(byte *)((int)param_2 + 2) = *(byte *)((uint)*(byte *)((int)param_2 + 2) + param_3);
          param_2 = (void *)((int)param_2 + 4);
        }
      }
      else {
        for (; iVar10 != 0; iVar10 = iVar10 + -1) {
          uVar3 = *(undefined2 *)
                   (*(int *)((int)param_4 +
                            (uint)(*(byte *)((int)param_2 + 1) >> ((byte)param_5 & 0x1f)) * 4) +
                   (uint)*(byte *)param_2 * 2);
          *(byte *)((int)param_2 + 1) = (byte)uVar3;
          *(byte *)param_2 = (byte)((ushort)uVar3 >> 8);
          uVar3 = *(undefined2 *)
                   (*(int *)((int)param_4 +
                            (uint)(*(byte *)((int)param_2 + 3) >> ((byte)param_5 & 0x1f)) * 4) +
                   (uint)*(byte *)((int)param_2 + 2) * 2);
          *(byte *)((int)param_2 + 3) = (byte)uVar3;
          *(byte *)((int)param_2 + 2) = (byte)((ushort)uVar3 >> 8);
          uVar3 = *(undefined2 *)
                   (*(int *)((int)param_4 +
                            (uint)(*(byte *)((int)param_2 + 5) >> ((byte)param_5 & 0x1f)) * 4) +
                   (uint)*(byte *)((int)param_2 + 4) * 2);
          *(byte *)((int)param_2 + 4) = (byte)((ushort)uVar3 >> 8);
          *(byte *)((int)param_2 + 5) = (byte)uVar3;
          param_2 = (void *)((int)param_2 + 8);
        }
      }
    }
  }
  return;
}
