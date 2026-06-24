/* address: 0x00591fc0 */
/* name: CDXTexture__Unk_00591fc0 */
/* signature: void __fastcall CDXTexture__Unk_00591fc0(int param_1) */


void __fastcall CDXTexture__Unk_00591fc0(int param_1)

{
  int iVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  byte bVar6;
  ushort uVar7;
  ushort uVar8;
  int iVar9;
  uint in_EAX;
  uint uVar10;
  int *unaff_ESI;
  char *unaff_EDI;

  iVar1 = in_EAX + param_1;
  if ((((in_EAX < 0xe) || (*unaff_EDI != 'J')) || (unaff_EDI[1] != 'F')) ||
     (((unaff_EDI[2] != 'I' || (unaff_EDI[3] != 'F')) || (unaff_EDI[4] != '\0')))) {
    if (((5 < in_EAX) && (*unaff_EDI == 'J')) &&
       ((unaff_EDI[1] == 'F' &&
        (((unaff_EDI[2] == 'X' && (unaff_EDI[3] == 'X')) && (unaff_EDI[4] == '\0')))))) {
      uVar10 = (uint)(byte)unaff_EDI[5];
      if (uVar10 == 0x10) {
        iVar9 = *unaff_ESI;
        *(undefined4 *)(iVar9 + 0x14) = 0x6c;
        *(int *)(iVar9 + 0x18) = iVar1;
        (**(code **)(iVar9 + 4))();
        return;
      }
      if (uVar10 != 0x11) {
        iVar9 = *unaff_ESI;
        if (uVar10 != 0x13) {
          *(undefined4 *)(iVar9 + 0x14) = 0x59;
          *(uint *)(iVar9 + 0x18) = uVar10;
          *(int *)(iVar9 + 0x1c) = iVar1;
          (**(code **)(iVar9 + 4))();
          return;
        }
        *(undefined4 *)(iVar9 + 0x14) = 0x6e;
        *(int *)(iVar9 + 0x18) = iVar1;
        (**(code **)(iVar9 + 4))();
        return;
      }
      iVar9 = *unaff_ESI;
      *(undefined4 *)(iVar9 + 0x14) = 0x6d;
      *(int *)(iVar9 + 0x18) = iVar1;
      (**(code **)(iVar9 + 4))();
      return;
    }
    iVar9 = *unaff_ESI;
    *(undefined4 *)(iVar9 + 0x14) = 0x4d;
    *(int *)(iVar9 + 0x18) = iVar1;
    (**(code **)(iVar9 + 4))();
  }
  else {
    bVar2 = unaff_EDI[5];
    *(char *)((int)unaff_ESI + 0x122) = unaff_EDI[7];
    bVar3 = unaff_EDI[8];
    bVar4 = unaff_EDI[6];
    bVar5 = unaff_EDI[9];
    unaff_ESI[0x47] = 1;
    *(byte *)(unaff_ESI + 0x48) = bVar2;
    *(byte *)((int)unaff_ESI + 0x121) = bVar4;
    bVar6 = unaff_EDI[0xb];
    *(ushort *)(unaff_ESI + 0x49) = (ushort)bVar3 * 0x100 + (ushort)bVar5;
    *(ushort *)((int)unaff_ESI + 0x126) = (ushort)(byte)unaff_EDI[10] * 0x100 + (ushort)bVar6;
    if (bVar2 != 1) {
      iVar9 = *unaff_ESI;
      *(undefined4 *)(iVar9 + 0x14) = 0x77;
      *(uint *)(iVar9 + 0x18) = (uint)bVar2;
      *(uint *)(iVar9 + 0x1c) = (uint)bVar4;
      (**(code **)(iVar9 + 4))();
    }
    iVar9 = *unaff_ESI;
    bVar2 = *(byte *)((int)unaff_ESI + 0x121);
    *(uint *)(iVar9 + 0x18) = (uint)*(byte *)(unaff_ESI + 0x48);
    uVar7 = *(ushort *)(unaff_ESI + 0x49);
    *(uint *)(iVar9 + 0x1c) = (uint)bVar2;
    uVar8 = *(ushort *)((int)unaff_ESI + 0x126);
    *(uint *)(iVar9 + 0x20) = (uint)uVar7;
    bVar2 = *(byte *)((int)unaff_ESI + 0x122);
    *(uint *)(iVar9 + 0x24) = (uint)uVar8;
    *(uint *)(iVar9 + 0x28) = (uint)bVar2;
    *(undefined4 *)(iVar9 + 0x14) = 0x57;
    (**(code **)(iVar9 + 4))();
    bVar2 = unaff_EDI[0xc];
    bVar3 = unaff_EDI[0xd];
    if (bVar2 != 0 || bVar3 != 0) {
      iVar9 = *unaff_ESI;
      *(undefined4 *)(iVar9 + 0x14) = 0x5a;
      *(uint *)(iVar9 + 0x18) = (uint)bVar2;
      *(uint *)(iVar9 + 0x1c) = (uint)bVar3;
      (**(code **)(iVar9 + 4))();
    }
    if (iVar1 + -0xe != (uint)(byte)unaff_EDI[0xc] * (uint)(byte)unaff_EDI[0xd] * 3) {
      iVar9 = *unaff_ESI;
      *(undefined4 *)(iVar9 + 0x14) = 0x58;
      *(int *)(iVar9 + 0x18) = iVar1 + -0xe;
      (**(code **)(iVar9 + 4))();
      return;
    }
  }
  return;
}
