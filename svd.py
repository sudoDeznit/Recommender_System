import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds 


# column headers for the dataset
data_cols = ['UserID', 'MovieID', 'Rating', 'Timestamp']
item_cols = ['MovieID', 'Title', 'release_date', 'video_release_date','IMDb_URL', 'unknown', 'Action', 'Adventure', 'Animation', 'Childrens', 'Comedy', 'Crime', 'Documentary', 'Drama','Fantasy','Film-Noir','Horror', 'Musical','Mystery','Romance ','Sci-Fi','Thriller', 'War', 'Western']
user_cols = ['UserID', 'age', 'gender', 'occupation', 'zip_code']

# importing the data files onto dataframes
ratings_list = pd.read_csv('./ml-100k/u.data', sep='\t', names=data_cols, encoding='latin-1')
movies_list = pd.read_csv('./ml-100k/u.item', sep='|', names=item_cols, encoding='latin-1')
users_list = pd.read_csv('./ml-100k/u.user', sep='|', names=user_cols, encoding='latin-1')

ratings = np.array(ratings_list)
users = np.array(users_list)
movies = np.array(movies_list)

ratings_df = pd.DataFrame(ratings_list, columns = ['UserID', 'MovieID', 'Rating', 'Timestamp'], dtype = int)
movies_df = pd.DataFrame(movies_list, columns = ['MovieID', 'Title', 'Genres'])
movies_df['MovieID'] = movies_df['MovieID'].apply(pd.to_numeric)

#print(movies_df.head())

R_df = ratings_df.pivot(index = 'UserID', columns ='MovieID', values = 'Rating').fillna(0)
#print(R_df.head())

R = R_df.as_matrix()
user_ratings_mean = np.mean(R, axis = 1)
R_demeaned = R - user_ratings_mean.reshape(-1, 1)

U, sigma, Vt = svds(R_demeaned, k = 50)


sigma = np.diag(sigma)

all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)

preds_df = pd.DataFrame(all_user_predicted_ratings, columns = R_df.columns)

print(preds_df.shape)


def recommend_movies(predictions_df, userID, movies_df, original_ratings_df, num_recommendations=5):
    
    # Get and sort the user's predictions
    user_row_number = userID - 1 # UserID starts at 1, not 0
    sorted_user_predictions = preds_df.iloc[user_row_number].sort_values(ascending=False) # UserID starts at 1
    
    # Get the user's data and merge in the movie information.
    user_data = original_ratings_df[original_ratings_df.UserID == (userID)]
    user_full = (user_data.merge(movies_df, how = 'left', left_on = 'MovieID', right_on = 'MovieID').
                     sort_values(['Rating'], ascending=False)
                 )

    print ('User {0} has already rated {1} movies.'.format(userID, user_full.shape[0]))
    print ('Recommending highest {0} predicted ratings movies not already rated.'.format(num_recommendations))
    
    # Recommend the highest predicted rating movies that the user hasn't seen yet.
    recommendations = (movies_df[~movies_df['MovieID'].isin(user_full['MovieID'])].
         merge(pd.DataFrame(sorted_user_predictions).reset_index(), how = 'left',
               left_on = 'MovieID',
               right_on = 'MovieID').
         rename(columns = {user_row_number: 'Predictions'}).
         sort_values('Predictions', ascending = False).
                       iloc[:num_recommendations, :-1]
                      )

    return user_full, recommendations

already_rated, predictions = recommend_movies(preds_df, 11, movies_df, ratings_df, 10)

print(predictions[:])