/* address: 0x0040d320 */
/* name: CMCBuggy__MultiplyMat34Basis */
/* signature: void __thiscall CMCBuggy__MultiplyMat34Basis(void * this, void * out_basis, void * lhs_basis, void * rhs_basis) */


void __thiscall
CMCBuggy__MultiplyMat34Basis(void *this,void *out_basis,void *lhs_basis,void *rhs_basis)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  float fVar26;
  float fVar27;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  float fVar32;
  float fVar33;
  float fVar34;
  float fVar35;
  float fVar36;
  float fVar37;
  float fVar38;
  float fVar39;
  float fVar40;
  float fVar41;
  float fVar42;
  float fVar43;
  float fVar44;
  float fVar45;
  float fVar46;
  float fVar47;
  float fVar48;
  undefined4 local_24;
  undefined4 local_14;
  undefined4 local_4;

  fVar1 = *(float *)((int)this + 0x28);
  fVar2 = *(float *)((int)lhs_basis + 0x20);
  fVar3 = *(float *)((int)this + 0x24);
  fVar4 = *(float *)((int)lhs_basis + 0x10);
  fVar5 = *(float *)((int)this + 0x20);
  fVar6 = *(float *)lhs_basis;
  fVar7 = *(float *)((int)this + 0x20);
  fVar8 = *(float *)((int)lhs_basis + 4);
  fVar9 = *(float *)((int)lhs_basis + 0x24);
  fVar10 = *(float *)((int)this + 0x28);
  fVar11 = *(float *)((int)this + 0x24);
  fVar12 = *(float *)((int)lhs_basis + 0x14);
  fVar13 = *(float *)((int)this + 0x28);
  fVar14 = *(float *)((int)lhs_basis + 0x28);
  fVar15 = *(float *)((int)this + 0x24);
  fVar16 = *(float *)((int)lhs_basis + 0x18);
  fVar17 = *(float *)((int)this + 0x20);
  fVar18 = *(float *)((int)lhs_basis + 8);
  fVar19 = *(float *)((int)this + 0x18);
  fVar20 = *(float *)((int)lhs_basis + 0x20);
  fVar21 = *(float *)((int)lhs_basis + 0x10);
  fVar22 = *(float *)((int)this + 0x14);
  fVar23 = *(float *)((int)this + 0x10);
  fVar24 = *(float *)lhs_basis;
  fVar25 = *(float *)((int)this + 0x10);
  fVar26 = *(float *)((int)lhs_basis + 4);
  fVar27 = *(float *)((int)lhs_basis + 0x24);
  fVar28 = *(float *)((int)this + 0x18);
  fVar29 = *(float *)((int)lhs_basis + 0x14);
  fVar30 = *(float *)((int)this + 0x14);
  fVar31 = *(float *)((int)lhs_basis + 8);
  fVar32 = *(float *)((int)this + 0x10);
  fVar33 = *(float *)((int)lhs_basis + 0x28);
  fVar34 = *(float *)((int)this + 0x18);
  fVar35 = *(float *)((int)lhs_basis + 0x18);
  fVar36 = *(float *)((int)this + 0x14);
  fVar37 = *(float *)((int)lhs_basis + 0x24);
  fVar38 = *(float *)((int)this + 8);
  fVar39 = *(float *)((int)lhs_basis + 0x14);
  fVar40 = *(float *)((int)this + 4);
  fVar41 = *(float *)this;
  fVar42 = *(float *)((int)lhs_basis + 4);
  fVar43 = *(float *)((int)lhs_basis + 0x28);
  fVar44 = *(float *)((int)this + 8);
  fVar45 = *(float *)((int)lhs_basis + 0x18);
  fVar46 = *(float *)((int)this + 4);
  fVar47 = *(float *)((int)lhs_basis + 8);
  fVar48 = *(float *)this;
  *(float *)out_basis =
       *(float *)((int)lhs_basis + 0x20) * *(float *)((int)this + 8) +
       *(float *)lhs_basis * *(float *)this +
       *(float *)((int)lhs_basis + 0x10) * *(float *)((int)this + 4);
  *(float *)((int)out_basis + 4) = fVar41 * fVar42 + fVar39 * fVar40 + fVar37 * fVar38;
  *(float *)((int)out_basis + 8) = fVar47 * fVar48 + fVar45 * fVar46 + fVar43 * fVar44;
  *(undefined4 *)((int)out_basis + 0xc) = local_24;
  *(float *)((int)out_basis + 0x10) = fVar23 * fVar24 + fVar21 * fVar22 + fVar19 * fVar20;
  *(float *)((int)out_basis + 0x14) = fVar29 * fVar30 + fVar27 * fVar28 + fVar25 * fVar26;
  *(float *)((int)out_basis + 0x18) = fVar35 * fVar36 + fVar33 * fVar34 + fVar31 * fVar32;
  *(undefined4 *)((int)out_basis + 0x1c) = local_14;
  *(float *)((int)out_basis + 0x20) = fVar5 * fVar6 + fVar3 * fVar4 + fVar1 * fVar2;
  *(float *)((int)out_basis + 0x24) = fVar11 * fVar12 + fVar9 * fVar10 + fVar7 * fVar8;
  *(float *)((int)out_basis + 0x28) = fVar17 * fVar18 + fVar15 * fVar16 + fVar13 * fVar14;
  *(undefined4 *)((int)out_basis + 0x2c) = local_4;
  return;
}
