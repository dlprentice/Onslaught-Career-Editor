/* address: 0x0055db72 */
/* name: CRT__EhVectorDestructorIterator_IfNoException */
/* signature: void CRT__EhVectorDestructorIterator_IfNoException(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__EhVectorDestructorIterator_IfNoException(void)

{
  int unaff_EBP;

  if (*(int *)(unaff_EBP + -0x1c) == 0) {
    eh_vector_destructor_iterator
              (*(void **)(unaff_EBP + 8),*(int *)(unaff_EBP + 0xc),*(int *)(unaff_EBP + 0x10),
               *(void **)(unaff_EBP + 0x14));
  }
  return;
}
