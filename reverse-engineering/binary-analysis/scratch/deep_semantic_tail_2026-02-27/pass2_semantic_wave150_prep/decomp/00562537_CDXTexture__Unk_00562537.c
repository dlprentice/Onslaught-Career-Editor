/* address: 0x00562537 */
/* name: CDXTexture__Unk_00562537 */
/* signature: int CDXTexture__Unk_00562537(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Unk_00562537(void)

{
  uint uVar1;
  uint *in_stack_00000004;
  uint *in_stack_00000008;
  uint in_stack_0000000c;
  uint in_stack_00000010;
  undefined8 *in_stack_00000014;
  undefined8 *in_stack_00000018;

  uVar1 = in_stack_0000000c;
  in_stack_00000004[1] = 0;
  in_stack_00000004[2] = 0;
  in_stack_00000004[3] = 0;
  if ((in_stack_0000000c & 0x10) != 0) {
    in_stack_0000000c = 0xc000008f;
    in_stack_00000004[1] = in_stack_00000004[1] | 1;
  }
  if ((uVar1 & 2) != 0) {
    in_stack_0000000c = 0xc0000093;
    in_stack_00000004[1] = in_stack_00000004[1] | 2;
  }
  if ((uVar1 & 1) != 0) {
    in_stack_0000000c = 0xc0000091;
    in_stack_00000004[1] = in_stack_00000004[1] | 4;
  }
  if ((uVar1 & 4) != 0) {
    in_stack_0000000c = 0xc000008e;
    in_stack_00000004[1] = in_stack_00000004[1] | 8;
  }
  if ((uVar1 & 8) != 0) {
    in_stack_0000000c = 0xc0000090;
    in_stack_00000004[1] = in_stack_00000004[1] | 0x10;
  }
  in_stack_00000004[2] = (~*in_stack_00000008 & 1) << 4 | in_stack_00000004[2] & 0xffffffef;
  in_stack_00000004[2] = (~*in_stack_00000008 & 4) << 1 | in_stack_00000004[2] & 0xfffffff7;
  in_stack_00000004[2] = ~*in_stack_00000008 >> 1 & 4 | in_stack_00000004[2] & 0xfffffffb;
  in_stack_00000004[2] = ~*in_stack_00000008 >> 3 & 2 | in_stack_00000004[2] & 0xfffffffd;
  in_stack_00000004[2] = ~*in_stack_00000008 >> 5 & 1 | in_stack_00000004[2] & 0xfffffffe;
  uVar1 = CDXTexture__Helper_00562c59();
  if ((uVar1 & 1) != 0) {
    in_stack_00000004[3] = in_stack_00000004[3] | 0x10;
  }
  if ((uVar1 & 4) != 0) {
    in_stack_00000004[3] = in_stack_00000004[3] | 8;
  }
  if ((uVar1 & 8) != 0) {
    in_stack_00000004[3] = in_stack_00000004[3] | 4;
  }
  if ((uVar1 & 0x10) != 0) {
    in_stack_00000004[3] = in_stack_00000004[3] | 2;
  }
  if ((uVar1 & 0x20) != 0) {
    in_stack_00000004[3] = in_stack_00000004[3] | 1;
  }
  uVar1 = *in_stack_00000008 & 0xc00;
  if (uVar1 == 0) {
    *in_stack_00000004 = *in_stack_00000004 & 0xfffffffc;
  }
  else {
    if (uVar1 == 0x400) {
      uVar1 = *in_stack_00000004 & 0xfffffffd | 1;
    }
    else {
      if (uVar1 != 0x800) {
        if (uVar1 == 0xc00) {
          *in_stack_00000004 = *in_stack_00000004 | 3;
        }
        goto LAB_005626ac;
      }
      uVar1 = *in_stack_00000004 & 0xfffffffe | 2;
    }
    *in_stack_00000004 = uVar1;
  }
LAB_005626ac:
  uVar1 = *in_stack_00000008 & 0x300;
  if (uVar1 == 0) {
    uVar1 = *in_stack_00000004 & 0xffffffeb | 8;
LAB_005626e2:
    *in_stack_00000004 = uVar1;
  }
  else {
    if (uVar1 == 0x200) {
      uVar1 = *in_stack_00000004 & 0xffffffe7 | 4;
      goto LAB_005626e2;
    }
    if (uVar1 == 0x300) {
      *in_stack_00000004 = *in_stack_00000004 & 0xffffffe3;
    }
  }
  *in_stack_00000004 = (in_stack_00000010 & 0xfff) << 5 | *in_stack_00000004 & 0xfffe001f;
  in_stack_00000004[8] = in_stack_00000004[8] | 1;
  in_stack_00000004[8] = in_stack_00000004[8] & 0xffffffe3 | 2;
  *(undefined8 *)(in_stack_00000004 + 4) = *in_stack_00000014;
  in_stack_00000004[0x14] = in_stack_00000004[0x14] | 1;
  in_stack_00000004[0x14] = in_stack_00000004[0x14] & 0xffffffe3 | 2;
  *(undefined8 *)(in_stack_00000004 + 0x10) = *in_stack_00000018;
  CDXTexture__Helper_00562c67();
  RaiseException(in_stack_0000000c,0,1,(ULONG_PTR *)&stack0x00000004);
  if ((in_stack_00000004[2] & 0x10) != 0) {
    *in_stack_00000008 = *in_stack_00000008 & 0xfffffffe;
  }
  if ((in_stack_00000004[2] & 8) != 0) {
    *in_stack_00000008 = *in_stack_00000008 & 0xfffffffb;
  }
  if ((in_stack_00000004[2] & 4) != 0) {
    *in_stack_00000008 = *in_stack_00000008 & 0xfffffff7;
  }
  if ((in_stack_00000004[2] & 2) != 0) {
    *in_stack_00000008 = *in_stack_00000008 & 0xffffffef;
  }
  if ((in_stack_00000004[2] & 1) != 0) {
    *in_stack_00000008 = *in_stack_00000008 & 0xffffffdf;
  }
  uVar1 = *in_stack_00000004 & 3;
  if (uVar1 == 0) {
    *in_stack_00000008 = *in_stack_00000008 & 0xfffff3ff;
  }
  else {
    if (uVar1 == 1) {
      uVar1 = *in_stack_00000008 & 0xfffff7ff | 0x400;
    }
    else {
      if (uVar1 != 2) {
        if (uVar1 == 3) {
          *(byte *)((int)in_stack_00000008 + 1) = *(byte *)((int)in_stack_00000008 + 1) | 0xc;
        }
        goto LAB_005627b7;
      }
      uVar1 = *in_stack_00000008 & 0xfffffbff | 0x800;
    }
    *in_stack_00000008 = uVar1;
  }
LAB_005627b7:
  uVar1 = *in_stack_00000004 >> 2 & 7;
  if (uVar1 == 0) {
    uVar1 = *in_stack_00000008 & 0xfffff3ff | 0x300;
  }
  else {
    if (uVar1 != 1) {
      if (uVar1 == 2) {
        *in_stack_00000008 = *in_stack_00000008 & 0xfffff3ff;
      }
      goto LAB_005627e0;
    }
    uVar1 = *in_stack_00000008 & 0xfffff3ff | 0x200;
  }
  *in_stack_00000008 = uVar1;
LAB_005627e0:
  *in_stack_00000018 = *(undefined8 *)(in_stack_00000004 + 0x10);
  return (int)in_stack_00000004;
}
