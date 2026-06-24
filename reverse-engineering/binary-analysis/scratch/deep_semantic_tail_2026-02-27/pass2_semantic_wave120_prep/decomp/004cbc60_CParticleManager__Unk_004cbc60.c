/* address: 0x004cbc60 */
/* name: CParticleManager__Unk_004cbc60 */
/* signature: void CParticleManager__Unk_004cbc60(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CParticleManager__Unk_004cbc60(void)

{
  int *piVar1;
  int iVar2;

  for (piVar1 = DAT_0082b404; piVar1 != (int *)0x0; piVar1 = (int *)piVar1[0x10]) {
    iVar2 = (**(code **)(*piVar1 + 4))();
    if (iVar2 == 0xb) {
      (**(code **)(*piVar1 + 0x5c))(0);
    }
  }
  RenderState_Set(0xf,1);
  return;
}
