/* address: 0x0059020b */
/* name: CTexture__ParseScriptWithYaccTables */
/* signature: int CTexture__ParseScriptWithYaccTables(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__ParseScriptWithYaccTables(void)

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

  _DAT_009d2410 = 0;
  DAT_009d240c = 0;
  DAT_009d2404 = (short *)&DAT_009d2010;
  DAT_009d2400 = (undefined4 *)&DAT_009d1840;
  iVar5 = 0;
  _DAT_009d2010 = 0;
LAB_0059023d:
  DAT_009d2408 = 0xffffffff;
LAB_00590242:
  iVar3 = (int)(short)(&DAT_00658438)[iVar5];
  if (iVar3 == 0) {
    if (((int)DAT_009d2408 < 0) &&
       (DAT_009d2408 = CTexture__Helper_0058f593(DAT_009d2418), (int)DAT_009d2408 < 0)) {
      DAT_009d2408 = 0;
    }
    if (((((short)(&DAT_00658580)[iVar5] != 0) &&
         (iVar3 = (int)(short)(&DAT_00658580)[iVar5] + DAT_009d2408, -1 < iVar3)) && (iVar3 < 0x128)
        ) && ((int)*(short *)(&DAT_00658a20 + iVar3 * 2) == DAT_009d2408)) {
      if (&DAT_009d23f6 <= DAT_009d2404) goto LAB_005906c7;
      iVar5 = (int)*(short *)(&DAT_006587d0 + iVar3 * 2);
      DAT_009d2404 = DAT_009d2404 + 1;
      *DAT_009d2404 = *(short *)(&DAT_006587d0 + iVar3 * 2);
      DAT_009d2400 = DAT_009d2400 + 1;
      *DAT_009d2400 = DAT_009d23f8;
      DAT_009d2408 = 0xffffffff;
      if (0 < DAT_009d240c) {
        DAT_009d240c = DAT_009d240c + -1;
      }
      goto LAB_00590242;
    }
    if ((((short)(&DAT_00658688)[iVar5] != 0) &&
        (iVar3 = (int)(short)(&DAT_00658688)[iVar5] + DAT_009d2408, -1 < iVar3)) &&
       ((iVar3 < 0x128 && ((int)*(short *)(&DAT_00658a20 + iVar3 * 2) == DAT_009d2408)))) {
      iVar3 = (int)*(short *)(&DAT_006587d0 + iVar3 * 2);
      goto LAB_00590328;
    }
    if (DAT_009d240c == 0) {
      CTexture__Helper_0058d763(DAT_009d2418,"syntax error");
      _DAT_009d2410 = _DAT_009d2410 + 1;
    }
    if (2 < DAT_009d240c) goto LAB_005906bb;
    DAT_009d240c = 3;
    while ((((short)(&DAT_00658580)[*DAT_009d2404] == 0 ||
            (iVar5 = (short)(&DAT_00658580)[*DAT_009d2404] + 0x100, iVar5 < 0)) ||
           ((0x127 < iVar5 || (*(short *)(&DAT_00658a20 + iVar5 * 2) != 0x100))))) {
      if (DAT_009d2404 < (short *)0x9d2011) {
        DAT_009d240c = 3;
        return 1;
      }
      DAT_009d2404 = DAT_009d2404 + -1;
      DAT_009d2400 = DAT_009d2400 + -1;
    }
    if ((short *)0x9d23f5 < DAT_009d2404) goto LAB_005906c7;
    sVar1 = *(short *)(&DAT_006587d0 + iVar5 * 2);
    DAT_009d2404 = DAT_009d2404 + 1;
    *DAT_009d2404 = sVar1;
    uVar2 = DAT_009d23f8;
  }
  else {
LAB_00590328:
    iVar5 = (int)*(short *)(&DAT_006583b8 + iVar3 * 2);
    DAT_009d23fc = DAT_009d2400[1 - iVar5];
    switch(iVar3) {
    case 1:
      uVar8 = 0;
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
      uVar8 = 1;
      pvVar7 = (void *)0x4;
      break;
    case 6:
      uVar8 = 1;
      pvVar7 = (void *)0x5;
      break;
    case 7:
      uVar8 = 0;
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
      uVar8 = 1;
      pvVar7 = (void *)0xa;
      break;
    case 0xc:
      uVar8 = 2;
      pvVar7 = (void *)0xb;
      break;
    case 0xd:
      uVar8 = 1;
      pvVar7 = (void *)0xc;
      break;
    case 0xe:
      uVar8 = 2;
      pvVar7 = (void *)0xd;
      break;
    case 0xf:
      uVar8 = 3;
      pvVar7 = (void *)0xe;
      break;
    case 0x10:
      uVar8 = 4;
      pvVar7 = (void *)0xf;
      break;
    case 0x11:
      uVar8 = 5;
      pvVar7 = (void *)0x10;
      break;
    case 0x12:
      uVar8 = 6;
      pvVar7 = (void *)0x11;
      break;
    case 0x13:
      uVar8 = 6;
      pvVar7 = (void *)0x12;
      break;
    case 0x14:
      uVar8 = 6;
      pvVar7 = (void *)0x13;
      break;
    case 0x15:
      uVar8 = 3;
      pvVar7 = (void *)0x14;
      break;
    case 0x16:
      uVar8 = 2;
      pvVar7 = (void *)0x15;
      break;
    case 0x17:
      uVar8 = 3;
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
      uVar8 = 1;
      pvVar7 = (void *)0x19;
      break;
    case 0x1b:
      uVar8 = 1;
      pvVar7 = (void *)0x1a;
      break;
    case 0x1c:
      uVar8 = 1;
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
      uVar8 = 1;
      pvVar7 = (void *)0x21;
      break;
    case 0x21:
      uVar8 = 2;
      pvVar7 = (void *)0x22;
      break;
    case 0x22:
      uVar8 = 1;
      pvVar7 = (void *)0x23;
      break;
    case 0x23:
      uVar8 = 2;
      pvVar7 = (void *)0x24;
      break;
    case 0x24:
      uVar8 = 1;
      pvVar7 = (void *)0x25;
      break;
    case 0x25:
      uVar8 = 1;
      pvVar7 = (void *)0x26;
      break;
    case 0x26:
      uVar8 = 0;
      pvVar7 = (void *)0x27;
      break;
    case 0x27:
      uVar8 = 0;
      pvVar7 = (void *)0x28;
      break;
    case 0x28:
      uVar8 = 1;
      pvVar7 = (void *)0x29;
      break;
    case 0x29:
      uVar8 = 1;
      pvVar7 = (void *)0x2a;
      break;
    case 0x2a:
      uVar8 = 1;
      pvVar7 = (void *)0x2b;
      break;
    case 0x2b:
      uVar8 = 1;
      pvVar7 = (void *)0x2c;
      break;
    case 0x2c:
      uVar8 = 1;
      pvVar7 = (void *)0x2d;
      break;
    case 0x2d:
      uVar8 = 1;
      pvVar7 = (void *)0x2e;
      break;
    case 0x2e:
      uVar8 = 1;
      pvVar7 = (void *)0x2f;
      break;
    case 0x2f:
      uVar8 = 1;
      pvVar7 = (void *)0x30;
      break;
    case 0x30:
      uVar8 = 1;
      pvVar7 = (void *)0x31;
      break;
    case 0x31:
      uVar8 = 0;
      pvVar7 = (void *)0x32;
      break;
    case 0x32:
      uVar8 = 0;
      pvVar7 = (void *)0x33;
      break;
    case 0x33:
      uVar8 = 0;
      pvVar7 = (void *)0x34;
      break;
    case 0x34:
      uVar8 = 0;
      pvVar7 = (void *)0x35;
      break;
    case 0x35:
      uVar8 = 0;
      pvVar7 = (void *)0x36;
      break;
    case 0x36:
      uVar8 = 0;
      pvVar7 = (void *)0x37;
      break;
    case 0x37:
      uVar8 = 0;
      pvVar7 = (void *)0x38;
      break;
    case 0x38:
      uVar8 = 0;
      pvVar7 = (void *)0x39;
      break;
    case 0x39:
      uVar8 = 0;
      pvVar7 = (void *)0x3a;
      break;
    case 0x3a:
      uVar8 = 0;
      pvVar7 = (void *)0x3b;
      break;
    case 0x3b:
      uVar8 = 0;
      pvVar7 = (void *)0x3c;
      break;
    case 0x3c:
      uVar8 = 0;
      pvVar7 = (void *)0x3d;
      break;
    case 0x3d:
      uVar8 = 0;
      pvVar7 = (void *)0x3e;
      break;
    case 0x3e:
      uVar8 = 0;
      pvVar7 = (void *)0x3f;
      break;
    default:
      goto switchD_00590352_default;
    }
    CTexture__Helper_0058fbc5(DAT_009d2418,pvVar7,uVar8,unaff_EDI);
switchD_00590352_default:
    DAT_009d2404 = DAT_009d2404 + -iVar5;
    iVar4 = (int)*DAT_009d2404;
    DAT_009d2400 = DAT_009d2400 + -iVar5;
    if ((iVar4 == 0) && (*(short *)(&DAT_00658338 + iVar3 * 2) == 0)) {
      DAT_009d2404 = DAT_009d2404 + 1;
      iVar5 = 0x10;
      *DAT_009d2404 = 0x10;
      DAT_009d2400 = DAT_009d2400 + 1;
      *DAT_009d2400 = DAT_009d23fc;
      bVar6 = DAT_009d2408 == 0;
      if ((int)DAT_009d2408 < 0) {
        DAT_009d2408 = CTexture__Helper_0058f593(DAT_009d2418);
        bVar6 = DAT_009d2408 == 0;
        if ((int)DAT_009d2408 < 0) {
          DAT_009d2408 = 0;
          bVar6 = true;
        }
      }
      if (bVar6) {
        return 0;
      }
      goto LAB_00590242;
    }
    iVar5 = *(short *)(&DAT_00658338 + iVar3 * 2) * 2;
    if ((((*(short *)(&DAT_00658790 + iVar5) == 0) ||
         (iVar3 = *(short *)(&DAT_00658790 + iVar5) + iVar4, iVar3 < 0)) || (0x127 < iVar3)) ||
       (*(short *)(&DAT_00658a20 + iVar3 * 2) != iVar4)) {
      sVar1 = *(short *)(&DAT_00658540 + iVar5);
    }
    else {
      sVar1 = *(short *)(&DAT_006587d0 + iVar3 * 2);
    }
    if ((short *)0x9d23f5 < DAT_009d2404) {
LAB_005906c7:
      CTexture__Helper_0058d763(DAT_009d2418,"yacc stack overflow");
      return 1;
    }
    DAT_009d2404 = DAT_009d2404 + 1;
    *DAT_009d2404 = sVar1;
    uVar2 = DAT_009d23fc;
  }
  iVar5 = (int)sVar1;
  DAT_009d2400 = DAT_009d2400 + 1;
  *DAT_009d2400 = uVar2;
  goto LAB_00590242;
LAB_005906bb:
  if (DAT_009d2408 == 0) {
    return 1;
  }
  goto LAB_0059023d;
}
