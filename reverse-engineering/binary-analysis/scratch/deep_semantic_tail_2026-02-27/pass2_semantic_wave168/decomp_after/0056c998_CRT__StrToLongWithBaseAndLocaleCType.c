/* address: 0x0056c998 */
/* name: CRT__StrToLongWithBaseAndLocaleCType */
/* signature: int CRT__StrToLongWithBaseAndLocaleCType(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CRT__StrToLongWithBaseAndLocaleCType(void)

{
  byte *pbVar1;
  void *pvVar2;
  uint uVar3;
  void *pvVar4;
  uint uVar5;
  int iVar6;
  undefined4 *puVar7;
  undefined *in_ECX;
  void *this;
  byte bVar8;
  uint unaff_EDI;
  byte *in_stack_00000004;
  int *in_stack_00000008;
  void *in_stack_0000000c;
  uint in_stack_00000010;
  undefined *puVar9;
  void *local_c;
  byte *local_8;

  local_c = (void *)0x0;
  bVar8 = *in_stack_00000004;
  pbVar1 = in_stack_00000004;
  while( true ) {
    local_8 = pbVar1 + 1;
    if (DAT_00653a9c < 2) {
      uVar3 = (byte)PTR_DAT_00653890[(uint)bVar8 * 2] & 8;
      in_ECX = PTR_DAT_00653890;
    }
    else {
      puVar9 = (undefined *)0x8;
      uVar3 = CTexture__Helper_00563951(in_ECX,(uint)bVar8,8,unaff_EDI);
      in_ECX = puVar9;
    }
    if (uVar3 == 0) break;
    bVar8 = *local_8;
    pbVar1 = local_8;
  }
  if (bVar8 == 0x2d) {
    in_stack_00000010 = in_stack_00000010 | 2;
LAB_0056c9f3:
    bVar8 = *local_8;
    local_8 = pbVar1 + 2;
  }
  else if (bVar8 == 0x2b) goto LAB_0056c9f3;
  if ((((int)in_stack_0000000c < 0) || (in_stack_0000000c == (void *)0x1)) ||
     (0x24 < (int)in_stack_0000000c)) {
    if (in_stack_00000008 != (int *)0x0) {
      *in_stack_00000008 = (int)in_stack_00000004;
    }
    return 0;
  }
  this = (void *)0x10;
  if (in_stack_0000000c == (void *)0x0) {
    if (bVar8 != 0x30) {
      in_stack_0000000c = (void *)0xa;
      goto LAB_0056ca5d;
    }
    if ((*local_8 != 0x78) && (*local_8 != 0x58)) {
      in_stack_0000000c = (void *)0x8;
      goto LAB_0056ca5d;
    }
    in_stack_0000000c = (void *)0x10;
  }
  if (((in_stack_0000000c == (void *)0x10) && (bVar8 == 0x30)) &&
     ((*local_8 == 0x78 || (*local_8 == 0x58)))) {
    bVar8 = local_8[1];
    local_8 = local_8 + 2;
  }
LAB_0056ca5d:
  pvVar4 = (void *)(0xffffffff / ZEXT48(in_stack_0000000c));
  do {
    uVar3 = (uint)bVar8;
    if (DAT_00653a9c < 2) {
      uVar5 = (byte)PTR_DAT_00653890[uVar3 * 2] & 4;
    }
    else {
      pvVar2 = (void *)0x4;
      uVar5 = CTexture__Helper_00563951(this,uVar3,4,unaff_EDI);
      this = pvVar2;
    }
    if (uVar5 == 0) {
      if (DAT_00653a9c < 2) {
        uVar3 = *(ushort *)(PTR_DAT_00653890 + uVar3 * 2) & 0x103;
      }
      else {
        uVar3 = CTexture__Helper_00563951(this,uVar3,0x103,unaff_EDI);
      }
      if (uVar3 == 0) {
LAB_0056cb09:
        local_8 = local_8 + -1;
        if ((in_stack_00000010 & 8) == 0) {
          if (in_stack_00000008 != (int *)0x0) {
            local_8 = in_stack_00000004;
          }
          local_c = (void *)0x0;
        }
        else if (((in_stack_00000010 & 4) != 0) ||
                (((in_stack_00000010 & 1) == 0 &&
                 ((((in_stack_00000010 & 2) != 0 && ((void *)0x80000000 < local_c)) ||
                  (((in_stack_00000010 & 2) == 0 && ((void *)0x7fffffff < local_c)))))))) {
          puVar7 = (undefined4 *)CTexture__Helper_00567aa8();
          *puVar7 = 0x22;
          if ((in_stack_00000010 & 1) == 0) {
            local_c = (void *)(((in_stack_00000010 & 2) != 0) + 0x7fffffff);
          }
          else {
            local_c = (void *)0xffffffff;
          }
        }
        if (in_stack_00000008 != (int *)0x0) {
          *in_stack_00000008 = (int)local_8;
        }
        if ((in_stack_00000010 & 2) == 0) {
          return (int)local_c;
        }
        return -(int)local_c;
      }
      iVar6 = CTexture__Helper_0055e673((int)(char)bVar8);
      this = (void *)(iVar6 + -0x37);
    }
    else {
      this = (void *)((char)bVar8 + -0x30);
    }
    if (in_stack_0000000c <= this) goto LAB_0056cb09;
    if ((local_c < pvVar4) ||
       ((local_c == pvVar4 && (this <= (void *)(0xffffffff % ZEXT48(in_stack_0000000c)))))) {
      local_c = (void *)((int)local_c * (int)in_stack_0000000c + (int)this);
      in_stack_00000010 = in_stack_00000010 | 8;
    }
    else {
      in_stack_00000010 = in_stack_00000010 | 0xc;
    }
    bVar8 = *local_8;
    local_8 = local_8 + 1;
  } while( true );
}
