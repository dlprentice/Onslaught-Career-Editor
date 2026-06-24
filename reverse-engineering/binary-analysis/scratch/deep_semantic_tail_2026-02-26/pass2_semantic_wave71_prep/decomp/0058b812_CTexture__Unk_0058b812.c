/* address: 0x0058b812 */
/* name: CTexture__Unk_0058b812 */
/* signature: int CTexture__Unk_0058b812(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Unk_0058b812(void)

{
  short sVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint unaff_EDI;
  bool bVar6;
  void *pvVar7;
  uint uVar8;

  iVar5 = 0;
  _DAT_009d1830 = 0;
  DAT_009d182c = 0;
  DAT_009d1824 = (short *)&DAT_009d1430;
  DAT_009d1820 = (undefined4 *)&DAT_009d0c60;
  _DAT_009d1430 = 0;
LAB_0058b842:
  DAT_009d1828 = -1;
LAB_0058b84a:
  iVar3 = (int)(short)(&DAT_00657b48)[iVar5];
  if (iVar3 == 0) {
    if ((DAT_009d1828 < 0) &&
       (DAT_009d1828 = CTexture__Helper_005898a4((int)DAT_009d1838), DAT_009d1828 < 0)) {
      DAT_009d1828 = 0;
    }
    if (((((short)(&DAT_00657c08)[iVar5] != 0) &&
         (iVar3 = (short)(&DAT_00657c08)[iVar5] + DAT_009d1828, -1 < iVar3)) && (iVar3 < 0x172)) &&
       (*(short *)(&DAT_00658050 + iVar3 * 2) == DAT_009d1828)) {
      if (&DAT_009d1816 <= DAT_009d1824) goto LAB_0058bc4f;
      iVar5 = (int)*(short *)(&DAT_00657d68 + iVar3 * 2);
      DAT_009d1824 = DAT_009d1824 + 1;
      *DAT_009d1824 = *(short *)(&DAT_00657d68 + iVar3 * 2);
      DAT_009d1820 = DAT_009d1820 + 1;
      *DAT_009d1820 = DAT_009d1818;
      DAT_009d1828 = -1;
      if (0 < DAT_009d182c) {
        DAT_009d182c = DAT_009d182c + -1;
      }
      goto LAB_0058b84a;
    }
    if ((((short)(&DAT_00657ca8)[iVar5] != 0) &&
        (iVar3 = (short)(&DAT_00657ca8)[iVar5] + DAT_009d1828, -1 < iVar3)) &&
       ((iVar3 < 0x172 && (*(short *)(&DAT_00658050 + iVar3 * 2) == DAT_009d1828)))) {
      iVar3 = (int)*(short *)(&DAT_00657d68 + iVar3 * 2);
      goto LAB_0058b931;
    }
    if (DAT_009d182c == 0) {
      CTexture__Helper_00589bd6((int)DAT_009d1838,"syntax error");
      _DAT_009d1830 = _DAT_009d1830 + 1;
    }
    if (2 < DAT_009d182c) goto LAB_0058bc46;
    DAT_009d182c = 3;
    while ((((short)(&DAT_00657c08)[*DAT_009d1824] == 0 ||
            (iVar5 = (short)(&DAT_00657c08)[*DAT_009d1824] + 0x100, iVar5 < 0)) ||
           ((0x171 < iVar5 || (*(short *)(&DAT_00658050 + iVar5 * 2) != 0x100))))) {
      if (DAT_009d1824 < (short *)0x9d1431) {
        DAT_009d182c = 3;
        return 1;
      }
      DAT_009d1824 = DAT_009d1824 + -1;
      DAT_009d1820 = DAT_009d1820 + -1;
    }
    if ((short *)0x9d1815 < DAT_009d1824) goto LAB_0058bc4f;
    sVar1 = *(short *)(&DAT_00657d68 + iVar5 * 2);
    DAT_009d1824 = DAT_009d1824 + 1;
    *DAT_009d1824 = sVar1;
    uVar2 = DAT_009d1818;
  }
  else {
LAB_0058b931:
    iVar5 = (int)*(short *)(&DAT_00657ae8 + iVar3 * 2);
    DAT_009d181c = DAT_009d1820[1 - iVar5];
    switch(iVar3) {
    case 1:
      uVar8 = 1;
      pvVar7 = (void *)0x0;
      break;
    case 2:
      uVar8 = 1;
      pvVar7 = (void *)0x1;
      break;
    case 3:
      uVar8 = 1;
      pvVar7 = (void *)0x2;
      break;
    case 4:
      uVar8 = 2;
      pvVar7 = (void *)0x3;
      break;
    case 5:
      uVar8 = 0;
      pvVar7 = (void *)0x4;
      break;
    case 6:
      uVar8 = 0;
      pvVar7 = (void *)0x5;
      break;
    case 7:
      uVar8 = 1;
      pvVar7 = (void *)0x6;
      break;
    case 8:
      uVar8 = 1;
      pvVar7 = (void *)0x7;
      break;
    case 9:
      uVar8 = 1;
      pvVar7 = (void *)0x8;
      break;
    case 10:
      uVar8 = 1;
      pvVar7 = (void *)0x9;
      break;
    case 0xb:
      uVar8 = 0;
      pvVar7 = (void *)0xa;
      break;
    case 0xc:
      uVar8 = 0;
      pvVar7 = (void *)0xb;
      break;
    case 0xd:
      uVar8 = 0;
      pvVar7 = (void *)0xc;
      break;
    case 0xe:
      uVar8 = 0;
      pvVar7 = (void *)0xd;
      break;
    case 0xf:
      uVar8 = 0;
      pvVar7 = (void *)0xe;
      break;
    case 0x10:
      uVar8 = 1;
      pvVar7 = (void *)0xf;
      break;
    case 0x11:
      uVar8 = 1;
      pvVar7 = (void *)0x10;
      break;
    case 0x12:
      uVar8 = 1;
      pvVar7 = (void *)0x11;
      break;
    case 0x13:
      uVar8 = 1;
      pvVar7 = (void *)0x12;
      break;
    case 0x14:
      uVar8 = 1;
      pvVar7 = (void *)0x13;
      break;
    case 0x15:
      uVar8 = 1;
      pvVar7 = (void *)0x14;
      break;
    case 0x16:
      uVar8 = 1;
      pvVar7 = (void *)0x15;
      break;
    case 0x17:
      uVar8 = 1;
      pvVar7 = (void *)0x16;
      break;
    case 0x18:
      uVar8 = 1;
      pvVar7 = (void *)0x17;
      break;
    case 0x19:
      uVar8 = 2;
      pvVar7 = (void *)0x18;
      break;
    case 0x1a:
      uVar8 = 2;
      pvVar7 = (void *)0x19;
      break;
    case 0x1b:
      uVar8 = 1;
      pvVar7 = (void *)0x1a;
      break;
    case 0x1c:
      uVar8 = 2;
      pvVar7 = (void *)0x1b;
      break;
    case 0x1d:
      uVar8 = 2;
      pvVar7 = (void *)0x1c;
      break;
    case 0x1e:
      uVar8 = 1;
      pvVar7 = (void *)0x1d;
      break;
    case 0x1f:
      uVar8 = 2;
      pvVar7 = (void *)0x1e;
      break;
    case 0x20:
      uVar8 = 2;
      pvVar7 = (void *)0x1f;
      break;
    case 0x21:
      uVar8 = 2;
      pvVar7 = (void *)0x20;
      break;
    case 0x22:
      uVar8 = 2;
      pvVar7 = (void *)0x21;
      break;
    case 0x23:
      uVar8 = 1;
      pvVar7 = (void *)0x22;
      break;
    case 0x24:
      uVar8 = 2;
      pvVar7 = (void *)0x23;
      break;
    case 0x25:
      uVar8 = 2;
      pvVar7 = (void *)0x24;
      break;
    case 0x26:
      uVar8 = 1;
      pvVar7 = (void *)0x25;
      break;
    case 0x27:
      uVar8 = 2;
      pvVar7 = (void *)0x26;
      break;
    case 0x28:
      uVar8 = 1;
      pvVar7 = (void *)0x27;
      break;
    case 0x29:
      uVar8 = 2;
      pvVar7 = (void *)0x28;
      break;
    case 0x2a:
      uVar8 = 1;
      pvVar7 = (void *)0x29;
      break;
    case 0x2b:
      uVar8 = 3;
      pvVar7 = (void *)0x2a;
      break;
    case 0x2c:
      uVar8 = 1;
      pvVar7 = (void *)0x2b;
      break;
    case 0x2d:
      uVar8 = 0;
      pvVar7 = (void *)0x2c;
      break;
    case 0x2e:
      uVar8 = 0;
      pvVar7 = (void *)0x2d;
      break;
    case 0x2f:
      uVar8 = 0;
      pvVar7 = (void *)0x2e;
      break;
    default:
      goto switchD_0058b95b_default;
    }
    CTexture__Unk_0058b3c7(DAT_009d1838,pvVar7,uVar8,unaff_EDI);
switchD_0058b95b_default:
    DAT_009d1824 = DAT_009d1824 + -iVar5;
    iVar4 = (int)*DAT_009d1824;
    DAT_009d1820 = DAT_009d1820 + -iVar5;
    if ((iVar4 == 0) && (*(short *)(&DAT_00657a88 + iVar3 * 2) == 0)) {
      DAT_009d1824 = DAT_009d1824 + 1;
      iVar5 = 0xf;
      *DAT_009d1824 = 0xf;
      DAT_009d1820 = DAT_009d1820 + 1;
      *DAT_009d1820 = DAT_009d181c;
      bVar6 = DAT_009d1828 == 0;
      if (DAT_009d1828 < 0) {
        DAT_009d1828 = CTexture__Helper_005898a4((int)DAT_009d1838);
        bVar6 = DAT_009d1828 == 0;
        if (DAT_009d1828 < 0) {
          DAT_009d1828 = 0;
          bVar6 = true;
        }
      }
      if (bVar6) {
        return 0;
      }
      goto LAB_0058b84a;
    }
    iVar5 = *(short *)(&DAT_00657a88 + iVar3 * 2) * 2;
    iVar3 = (int)*(short *)((int)&PTR_DAT_00657d48 + iVar5);
    if ((((iVar3 == 0) || (iVar3 = iVar3 + iVar4, iVar3 < 0)) || (0x171 < iVar3)) ||
       (*(short *)(&DAT_00658050 + iVar3 * 2) != iVar4)) {
      sVar1 = *(short *)(&DAT_00657be8 + iVar5);
    }
    else {
      sVar1 = *(short *)(&DAT_00657d68 + iVar3 * 2);
    }
    if ((short *)0x9d1815 < DAT_009d1824) {
LAB_0058bc4f:
      CTexture__Helper_00589bd6((int)DAT_009d1838,"yacc stack overflow");
      return 1;
    }
    DAT_009d1824 = DAT_009d1824 + 1;
    *DAT_009d1824 = sVar1;
    uVar2 = DAT_009d181c;
  }
  iVar5 = (int)sVar1;
  DAT_009d1820 = DAT_009d1820 + 1;
  *DAT_009d1820 = uVar2;
  goto LAB_0058b84a;
LAB_0058bc46:
  if (DAT_009d1828 == 0) {
    return 1;
  }
  goto LAB_0058b842;
}
