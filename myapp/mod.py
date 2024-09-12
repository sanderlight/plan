class Goal(models.Model):
    goal_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE,default=None)

    def __str__(self):
        return self.goal_text
    
    
    
    
    