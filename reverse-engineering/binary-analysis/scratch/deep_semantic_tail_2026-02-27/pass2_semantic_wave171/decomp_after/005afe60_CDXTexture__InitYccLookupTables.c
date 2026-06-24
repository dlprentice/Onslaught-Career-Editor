/* address: 0x005afe60 */
/* name: CDXTexture__InitYccLookupTables */
/* signature: void CDXTexture__InitYccLookupTables(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__InitYccLookupTables(void)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int in_EAX;
  undefined4 uVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  int iVar15;
  int iVar16;

  iVar1 = *(int *)(in_EAX + 0x1cc);
  uVar11 = (*(code *)**(undefined4 **)(in_EAX + 4))();
  puVar2 = *(undefined4 **)(in_EAX + 4);
  *(undefined4 *)(iVar1 + 0x18) = uVar11;
  uVar11 = (*(code *)*puVar2)();
  puVar2 = *(undefined4 **)(in_EAX + 4);
  *(undefined4 *)(iVar1 + 0x1c) = uVar11;
  uVar11 = (*(code *)*puVar2)();
  *(undefined4 *)(iVar1 + 0x20) = uVar11;
  uVar11 = (*(code *)**(undefined4 **)(in_EAX + 4))();
  puVar2 = *(undefined4 **)(in_EAX + 4);
  *(undefined4 *)(iVar1 + 0x24) = uVar11;
  uVar11 = (*(code *)*puVar2)();
  puVar2 = *(undefined4 **)(in_EAX + 4);
  *(undefined4 *)(iVar1 + 0x28) = uVar11;
  uVar11 = (*(code *)*puVar2)();
  *(undefined4 *)(iVar1 + 0x2c) = uVar11;
  uVar11 = (*(code *)**(undefined4 **)(in_EAX + 4))();
  puVar2 = *(undefined4 **)(in_EAX + 4);
  *(undefined4 *)(iVar1 + 0x30) = uVar11;
  uVar11 = (*(code *)*puVar2)();
  puVar2 = *(undefined4 **)(in_EAX + 4);
  *(undefined4 *)(iVar1 + 0x34) = uVar11;
  uVar11 = (*(code *)*puVar2)();
  *(undefined4 *)(iVar1 + 0x38) = uVar11;
  iVar12 = (*(code *)**(undefined4 **)(in_EAX + 4))();
  iVar3 = *(int *)(iVar1 + 0x18);
  iVar4 = *(int *)(iVar1 + 0x30);
  *(int *)(iVar1 + 0x3c) = iVar12;
  iVar5 = *(int *)(iVar1 + 0x1c);
  iVar6 = *(int *)(iVar1 + 0x20);
  iVar7 = *(int *)(iVar1 + 0x24);
  iVar8 = *(int *)(iVar1 + 0x28);
  iVar9 = *(int *)(iVar1 + 0x2c);
  iVar15 = 0;
  iVar10 = *(int *)(iVar1 + 0x34);
  iVar1 = *(int *)(iVar1 + 0x38);
  do {
    if (iVar15 < 0xc0) {
      iVar16 = iVar15 * 0xdf;
      iVar13 = 0xfe81;
    }
    else {
      iVar16 = (iVar15 * 0x57c0 + -0x41cfe1) / 0x3f;
      iVar13 = 0x57c0;
    }
    *(int *)(iVar3 + iVar15 * 4) = iVar13 - iVar16;
    if (iVar15 < 0xc0) {
      iVar16 = iVar15 * 0xce;
      iVar13 = 0xfe81;
    }
    else {
      iVar16 = (iVar15 * 0x6480 + -0x4b5fe1) / 0x3f;
      iVar13 = 0x6480;
    }
    *(uint *)(iVar5 + iVar15 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar15 < 0xc0) {
      iVar16 = iVar15 * 0x5e;
      iVar13 = 0xfe81;
    }
    else {
      iVar16 = (iVar15 * 0x2019 + -0x1812a1) / 0x3f;
      iVar13 = 0xb880;
    }
    *(uint *)(iVar6 + iVar15 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar15 < 0xc0) {
      iVar16 = 0xfe81;
    }
    else {
      iVar16 = 0xff00 - (iVar15 * 0xbf4 + -0x8f6e1) / 0x3f;
    }
    *(uint *)(iVar7 + iVar15 * 4) = (uint)(iVar16 * 0x10101) >> 0x10;
    if (iVar15 < 0xc0) {
      iVar16 = iVar15 * 0x18;
      iVar13 = 0xfe81;
    }
    else {
      iVar16 = (iVar15 * 0x1dd0 + -0x165be1) / 0x3f;
      iVar13 = 0xed00;
    }
    *(uint *)(iVar8 + iVar15 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar15 < 0xc0) {
      iVar16 = iVar15 * 0xba;
      iVar13 = 0xfe81;
    }
    else {
      iVar16 = (iVar15 * 0x7380 + -0x569fe1) / 0x3f;
      iVar13 = 0x7380;
    }
    *(uint *)(iVar9 + iVar15 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar15 < 0xc0) {
      iVar16 = iVar15 * 0x84;
      iVar13 = 0xfe81;
    }
    else {
      iVar16 = (iVar15 * 0x2c70 + -0x2153e1) / 0x3f;
      iVar13 = 0x9c00;
    }
    *(uint *)(iVar4 + iVar15 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    *(uint *)(iVar10 + iVar15 * 4) = (((0xbf < iVar15) - 1 & 0xffffff81) + 0xff00) * 0x10101 >> 0x10
    ;
    if (iVar15 < 0xc0) {
      iVar16 = iVar15 * 7;
      iVar13 = 0xfe81;
    }
    else {
      iVar16 = (iVar15 * 0x5b5 + -0x447a1) / 0x3f;
      iVar13 = 0xf9c0;
    }
    *(uint *)(iVar1 + iVar15 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar15 < 0xc0) {
      iVar16 = iVar15 * 0xab;
      iVar13 = 0xfe81;
    }
    else {
      iVar16 = (iVar15 * 0x62dc + -0x4a24e1) / 0x3f;
      iVar13 = 0x7ec0;
    }
    iVar14 = iVar15 + 1;
    *(uint *)(iVar12 + iVar15 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 0xdf;
      iVar13 = 0xfda2;
    }
    else {
      iVar16 = (iVar15 * 0x57c0 + -0x417821) / 0x3f;
      iVar13 = 0x57c0;
    }
    *(int *)(iVar3 + 4 + iVar15 * 4) = iVar13 - iVar16;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 0xce;
      iVar13 = 0xfdb3;
    }
    else {
      iVar16 = (iVar15 * 0x6480 + -0x4afb61) / 0x3f;
      iVar13 = 0x6480;
    }
    *(uint *)(iVar5 + 4 + iVar15 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 0x5e;
      iVar13 = 0xfe23;
    }
    else {
      iVar16 = (iVar15 * 0x2019 + -0x17f288) / 0x3f;
      iVar13 = 0xb880;
    }
    *(uint *)(iVar6 + 4 + iVar15 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = 0xfe81;
    }
    else {
      iVar16 = 0xff00 - (iVar15 * 0xbf4 + -0x8eaed) / 0x3f;
    }
    *(uint *)(iVar7 + 4 + iVar15 * 4) = (uint)(iVar16 * 0x10101) >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 0x18;
      iVar13 = 0xfe69;
    }
    else {
      iVar16 = (iVar15 * 0x1dd0 + -0x163e11) / 0x3f;
      iVar13 = 0xed00;
    }
    *(uint *)(iVar8 + 4 + iVar15 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 0xba;
      iVar13 = 0xfdc7;
    }
    else {
      iVar16 = (iVar15 * 0x7380 + -0x562c61) / 0x3f;
      iVar13 = 0x7380;
    }
    *(uint *)(iVar9 + 4 + iVar15 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 0x84;
      iVar13 = 0xfdfd;
    }
    else {
      iVar16 = (iVar15 * 0x2c70 + -0x212771) / 0x3f;
      iVar13 = 0x9c00;
    }
    *(uint *)(iVar4 + 4 + iVar15 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    *(uint *)(iVar10 + 4 + iVar15 * 4) =
         (((0xbf < iVar14) - 1 & 0xffffff81) + 0xff00) * 0x10101 >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 7;
      iVar13 = 0xfe7a;
    }
    else {
      iVar16 = (iVar15 * 0x5b5 + -0x441ec) / 0x3f;
      iVar13 = 0xf9c0;
    }
    *(uint *)(iVar1 + 4 + iVar15 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 0xab;
      iVar13 = 0xfdd6;
    }
    else {
      iVar16 = (iVar15 * 0x62dc + -0x49c205) / 0x3f;
      iVar13 = 0x7ec0;
    }
    iVar14 = iVar15 + 2;
    *(uint *)(iVar12 + 4 + iVar15 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 0xdf;
      iVar13 = 0xfcc3;
    }
    else {
      iVar16 = (iVar15 * 0x57c0 + -0x412061) / 0x3f;
      iVar13 = 0x57c0;
    }
    *(int *)(iVar3 + iVar14 * 4) = iVar13 - iVar16;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 0xce;
      iVar13 = 0xfce5;
    }
    else {
      iVar16 = (iVar15 * 0x6480 + -0x4a96e1) / 0x3f;
      iVar13 = 0x6480;
    }
    *(uint *)(iVar5 + iVar14 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 0x5e;
      iVar13 = 0xfdc5;
    }
    else {
      iVar16 = (iVar15 * 0x2019 + -0x17d26f) / 0x3f;
      iVar13 = 0xb880;
    }
    *(uint *)(iVar6 + iVar14 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = 0xfe81;
    }
    else {
      iVar16 = 0xff00 - (iVar15 * 0xbf4 + -0x8def9) / 0x3f;
    }
    *(uint *)(iVar7 + iVar14 * 4) = (uint)(iVar16 * 0x10101) >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 0x18;
      iVar13 = 0xfe51;
    }
    else {
      iVar16 = (iVar15 * 0x1dd0 + -0x162041) / 0x3f;
      iVar13 = 0xed00;
    }
    *(uint *)(iVar8 + iVar14 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 0xba;
      iVar13 = 0xfd0d;
    }
    else {
      iVar16 = (iVar15 * 0x7380 + -0x55b8e1) / 0x3f;
      iVar13 = 0x7380;
    }
    *(uint *)(iVar9 + iVar14 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 0x84;
      iVar13 = 0xfd79;
    }
    else {
      iVar16 = (iVar15 * 0x2c70 + -0x20fb01) / 0x3f;
      iVar13 = 0x9c00;
    }
    *(uint *)(iVar4 + iVar14 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    *(uint *)(iVar10 + iVar14 * 4) = (((0xbf < iVar14) - 1 & 0xffffff81) + 0xff00) * 0x10101 >> 0x10
    ;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 7;
      iVar13 = 0xfe73;
    }
    else {
      iVar16 = (iVar15 * 0x5b5 + -0x43c37) / 0x3f;
      iVar13 = 0xf9c0;
    }
    *(uint *)(iVar1 + iVar14 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    if (iVar14 < 0xc0) {
      iVar16 = iVar15 * 0xab;
      iVar13 = 0xfd2b;
    }
    else {
      iVar16 = (iVar15 * 0x62dc + -0x495f29) / 0x3f;
      iVar13 = 0x7ec0;
    }
    *(uint *)(iVar12 + iVar14 * 4) = (uint)((iVar13 - iVar16) * 0x10101) >> 0x10;
    iVar16 = iVar15 + 3;
    if (iVar16 < 0xc0) {
      iVar13 = iVar15 * 0xdf;
      iVar14 = 0xfbe4;
    }
    else {
      iVar13 = (iVar15 * 0x57c0 + -0x40c8a1) / 0x3f;
      iVar14 = 0x57c0;
    }
    *(int *)(iVar3 + iVar16 * 4) = iVar14 - iVar13;
    if (iVar16 < 0xc0) {
      iVar13 = iVar15 * 0xce;
      iVar14 = 0xfc17;
    }
    else {
      iVar13 = (iVar15 * 0x6480 + -0x4a3261) / 0x3f;
      iVar14 = 0x6480;
    }
    *(uint *)(iVar5 + iVar16 * 4) = (uint)((iVar14 - iVar13) * 0x10101) >> 0x10;
    if (iVar16 < 0xc0) {
      iVar13 = iVar15 * 0x5e;
      iVar14 = 0xfd67;
    }
    else {
      iVar13 = (iVar15 * 0x2019 + -0x17b256) / 0x3f;
      iVar14 = 0xb880;
    }
    *(uint *)(iVar6 + iVar16 * 4) = (uint)((iVar14 - iVar13) * 0x10101) >> 0x10;
    if (iVar16 < 0xc0) {
      iVar13 = 0xfe81;
    }
    else {
      iVar13 = 0xff00 - (iVar15 * 0xbf4 + -0x8d305) / 0x3f;
    }
    *(uint *)(iVar7 + iVar16 * 4) = (uint)(iVar13 * 0x10101) >> 0x10;
    if (iVar16 < 0xc0) {
      iVar13 = iVar15 * 0x18;
      iVar14 = 0xfe39;
    }
    else {
      iVar13 = (iVar15 * 0x1dd0 + -0x160271) / 0x3f;
      iVar14 = 0xed00;
    }
    *(uint *)(iVar8 + iVar16 * 4) = (uint)((iVar14 - iVar13) * 0x10101) >> 0x10;
    if (iVar16 < 0xc0) {
      iVar13 = iVar15 * 0xba;
      iVar14 = 0xfc53;
    }
    else {
      iVar13 = (iVar15 * 0x7380 + -0x554561) / 0x3f;
      iVar14 = 0x7380;
    }
    *(uint *)(iVar9 + iVar16 * 4) = (uint)((iVar14 - iVar13) * 0x10101) >> 0x10;
    if (iVar16 < 0xc0) {
      iVar13 = iVar15 * 0x84;
      iVar14 = 0xfcf5;
    }
    else {
      iVar13 = (iVar15 * 0x2c70 + -0x20ce91) / 0x3f;
      iVar14 = 0x9c00;
    }
    *(uint *)(iVar4 + iVar16 * 4) = (uint)((iVar14 - iVar13) * 0x10101) >> 0x10;
    *(uint *)(iVar10 + iVar16 * 4) = (((0xbf < iVar16) - 1 & 0xffffff81) + 0xff00) * 0x10101 >> 0x10
    ;
    if (iVar16 < 0xc0) {
      iVar13 = iVar15 * 7;
      iVar14 = 0xfe6c;
    }
    else {
      iVar13 = (iVar15 * 0x5b5 + -0x43682) / 0x3f;
      iVar14 = 0xf9c0;
    }
    *(uint *)(iVar1 + iVar16 * 4) = (uint)((iVar14 - iVar13) * 0x10101) >> 0x10;
    if (iVar16 < 0xc0) {
      iVar13 = iVar15 * 0xab;
      iVar14 = 0xfc80;
    }
    else {
      iVar13 = (iVar15 * 0x62dc + -0x48fc4d) / 0x3f;
      iVar14 = 0x7ec0;
    }
    iVar15 = iVar15 + 4;
    *(uint *)(iVar12 + iVar16 * 4) = (uint)((iVar14 - iVar13) * 0x10101) >> 0x10;
  } while (iVar15 < 0x100);
  return;
}
